"""
Import songs from 2026a2_songs.json into the DynamoDB music table.

Run from project root:
    python -m database.import_music_data

This import preserves all song records, including repeated song titles,
by using artist as the partition key and title_year_album as the sort key.
"""

import json

import boto3
from botocore.exceptions import ClientError

from database.db_config import (
    AWS_REGION,
    MUSIC_TABLE,
    SONGS_JSON_PATH,
    build_music_sort_key,
    build_title_index_sort_key,
    build_year_album_lsi_sort_key,
    build_song_id,
)


def load_songs():
    if not SONGS_JSON_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {SONGS_JSON_PATH}")

    with open(SONGS_JSON_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    songs = data.get("songs")

    if not isinstance(songs, list):
        raise ValueError("JSON file must contain a 'songs' list.")

    return songs


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def build_music_item(song):
    title = clean(song.get("title"))
    artist = clean(song.get("artist"))
    year = clean(song.get("year"))
    album = clean(song.get("album"))
    img_url = clean(song.get("img_url"))

    song_id = build_song_id(title, artist, year, album)

    return {
        "artist": artist,
        "title_year_album": build_music_sort_key(title, year, album),
        "title": title,
        "year": year,
        "album": album,
        "img_url": img_url,
        "song_id": song_id,
        "artist_year_album": build_title_index_sort_key(artist, year, album),
        "year_album_title": build_year_album_lsi_sort_key(year, album, title),
    }


def import_music_data():
    songs = load_songs()

    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    table = dynamodb.Table(MUSIC_TABLE)

    inserted_count = 0
    skipped_count = 0

    for song in songs:
        item = build_music_item(song)

        try:
            table.put_item(
                Item=item,
                ConditionExpression=(
                    "attribute_not_exists(artist) "
                    "AND attribute_not_exists(title_year_album)"
                ),
            )
            inserted_count += 1
        except ClientError as error:
            if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
                skipped_count += 1
            else:
                raise

    print(f"Source records found: {len(songs)}")
    print(f"Inserted records: {inserted_count}")
    print(f"Skipped existing records: {skipped_count}")
    print(f"Target table: {MUSIC_TABLE}")


if __name__ == "__main__":
    import_music_data()
