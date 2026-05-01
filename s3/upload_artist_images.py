"""
Download artist images from 2026a2_songs.json, upload them to S3,
and update the DynamoDB music table with s3_image_key.

Run from project root:
    python -m s3.upload_artist_images

Cost control:
- Uploads only unique image URLs.
- Reuses the same S3 object key for songs by the same artist.
"""

import json
import re
from pathlib import Path
from urllib.parse import urlparse

import boto3
import requests
from boto3.dynamodb.conditions import Key

from backend.config import (
    AWS_REGION,
    S3_BUCKET_NAME,
    S3_IMAGE_PREFIX,
    MUSIC_TABLE,
)
from database.db_config import SONGS_JSON_PATH, build_music_sort_key

TEMP_IMAGE_DIR = Path("tmp_artist_images")


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def safe_filename(value):
    """
    Creates a safe file name from artist name or URL filename.
    """
    value = clean(value)
    value = re.sub(r"[^A-Za-z0-9._-]+", "", value)
    return value or "image"


def load_songs():
    with open(SONGS_JSON_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    songs = data.get("songs", [])

    if not isinstance(songs, list):
        raise ValueError("2026a2_songs.json must contain a songs list.")

    return songs


def get_image_extension(img_url):
    path = urlparse(img_url).path
    suffix = Path(path).suffix.lower()

    if suffix in [".jpg", ".jpeg", ".png", ".webp"]:
        return suffix

    return ".jpg"


def build_s3_key(artist, img_url):
    extension = get_image_extension(img_url)
    artist_name = safe_filename(artist)
    return f"{S3_IMAGE_PREFIX}{artist_name}{extension}"


def unique_artist_images(songs):
    """
    Returns one image URL per artist.
    The dataset analysis confirmed one image URL per artist.
    """
    image_map = {}

    for song in songs:
        artist = clean(song.get("artist"))
        img_url = clean(song.get("img_url"))

        if artist and img_url:
            image_map[artist] = img_url

    return image_map


def create_bucket_if_needed(s3_client):
    """
    Creates the S3 bucket if it does not already exist.
    """
    if not S3_BUCKET_NAME:
        raise ValueError("S3_BUCKET_NAME is not set in .env")

    existing_buckets = s3_client.list_buckets().get("Buckets", [])
    existing_names = [bucket["Name"] for bucket in existing_buckets]

    if S3_BUCKET_NAME in existing_names:
        print(f"S3 bucket already exists: {S3_BUCKET_NAME}")
        return

    print(f"Creating S3 bucket: {S3_BUCKET_NAME}")

    if AWS_REGION == "us-east-1":
        s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
    else:
        s3_client.create_bucket(
            Bucket=S3_BUCKET_NAME,
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
        )

    print(f"Created S3 bucket: {S3_BUCKET_NAME}")


def download_image(img_url, local_path):
    response = requests.get(img_url, timeout=20)
    response.raise_for_status()

    with open(local_path, "wb") as file:
        file.write(response.content)


def upload_image_to_s3(s3_client, local_path, s3_key):
    """
    Uploads an image to S3.

    ACL is intentionally not set here. Access strategy can be controlled by
    bucket policy or presigned URLs later depending on deployment decision.
    """
    content_type = "image/jpeg"

    if local_path.suffix.lower() == ".png":
        content_type = "image/png"
    elif local_path.suffix.lower() == ".webp":
        content_type = "image/webp"

    s3_client.upload_file(
        Filename=str(local_path),
        Bucket=S3_BUCKET_NAME,
        Key=s3_key,
        ExtraArgs={"ContentType": content_type},
    )


def update_music_records_with_s3_keys(songs, artist_to_s3_key):
    """
    Updates every music record with its matching S3 image key.
    """
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    table = dynamodb.Table(MUSIC_TABLE)

    updated_count = 0

    for song in songs:
        artist = clean(song.get("artist"))
        title = clean(song.get("title"))
        year = clean(song.get("year"))
        album = clean(song.get("album"))

        s3_key = artist_to_s3_key.get(artist)

        if not s3_key:
            continue

        table.update_item(
            Key={
                "artist": artist,
                "title_year_album": build_music_sort_key(title, year, album),
            },
            UpdateExpression="SET s3_image_key = :s3key",
            ExpressionAttributeValues={
                ":s3key": s3_key,
            },
        )

        updated_count += 1

    print(f"Updated music records with S3 image keys: {updated_count}")


def upload_artist_images():
    songs = load_songs()
    artist_images = unique_artist_images(songs)

    print(f"Unique artist images found: {len(artist_images)}")

    s3_client = boto3.client("s3", region_name=AWS_REGION)
    create_bucket_if_needed(s3_client)

    TEMP_IMAGE_DIR.mkdir(exist_ok=True)

    artist_to_s3_key = {}
    uploaded_count = 0
    failed_count = 0

    for artist, img_url in sorted(artist_images.items()):
        s3_key = build_s3_key(artist, img_url)
        local_path = TEMP_IMAGE_DIR / Path(s3_key).name

        try:
            print(f"Processing: {artist}")
            download_image(img_url, local_path)
            upload_image_to_s3(s3_client, local_path, s3_key)

            artist_to_s3_key[artist] = s3_key
            uploaded_count += 1

        except Exception as error:
            failed_count += 1
            print(f"Failed for {artist}: {error}")

    update_music_records_with_s3_keys(songs, artist_to_s3_key)

    print("\nS3 image upload complete.")
    print(f"Uploaded images: {uploaded_count}")
    print(f"Failed images: {failed_count}")
    print(f"S3 bucket: {S3_BUCKET_NAME}")
    print(f"S3 prefix: {S3_IMAGE_PREFIX}")


if __name__ == "__main__":
    upload_artist_images()
