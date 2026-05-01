"""
Music service.

Handles song search logic for the query area of the application.

Search supports:
- title
- artist
- year
- album

Multiple fields are combined using AND logic.
"""

from boto3.dynamodb.conditions import Key, Attr

from backend.config import (
    MUSIC_TABLE,
    MUSIC_TITLE_INDEX,
    MUSIC_YEAR_ALBUM_INDEX,
)
from backend.services.dynamodb_service import (
    query_items,
    scan_items,
    combine_filters,
)
from backend.services.s3_service import generate_presigned_image_url


def clean(value):
    """
    Normalise input values from frontend query parameters.
    """
    if value is None:
        return ""
    return str(value).strip()


def serialise_music_item(item):
    """
    Converts a DynamoDB music item into a frontend-friendly response object.

    image_url is the URL the frontend should use for display.
    It prefers a secure temporary S3 presigned URL and falls back to the
    original dataset img_url if an S3 key is unavailable.
    """
    s3_image_key = item.get("s3_image_key", "")

    return {
        "song_id": item.get("song_id"),
        "title": item.get("title"),
        "artist": item.get("artist"),
        "year": item.get("year"),
        "album": item.get("album"),
        "img_url": item.get("img_url"),
        "s3_image_key": s3_image_key,
        "image_url": generate_presigned_image_url(s3_image_key) or item.get("img_url"),
    }


def build_non_key_filters(year="", album="", artist="", title=""):
    """
    Builds AND filters for non-key fields.
    These are used after a Query or during a controlled Scan.
    """
    filters = []

    if year:
        filters.append(Attr("year").eq(year))

    if album:
        filters.append(Attr("album").eq(album))

    if artist:
        filters.append(Attr("artist").eq(artist))

    if title:
        filters.append(Attr("title").eq(title))

    return combine_filters(filters)


def search_music(title="", artist="", year="", album=""):
    """
    Searches music records using AND semantics.

    Query strategy:
    1. If artist is provided, query the main table by artist.
       - If year is also provided, use the LSI with begins_with(year#).
       - Other fields are applied as filters.
    2. If title is provided but artist is not, query the title-index GSI.
       - Other fields are applied as filters.
    3. If only year/album is provided, use controlled Scan with filters.

    Returns:
        list[dict]
    """
    title = clean(title)
    artist = clean(artist)
    year = clean(year)
    album = clean(album)

    if not any([title, artist, year, album]):
        return []

    # Case 1: Artist-based query. This supports likely marker queries well.
    if artist:
        if year:
            filter_expression = build_non_key_filters(
                album=album,
                title=title,
            )

            items = query_items(
                MUSIC_TABLE,
                key_condition_expression=Key("artist").eq(artist)
                & Key("year_album_title").begins_with(f"{year}#"),
                index_name=MUSIC_YEAR_ALBUM_INDEX,
                filter_expression=filter_expression,
            )
        else:
            filter_expression = build_non_key_filters(
                year=year,
                album=album,
                title=title,
            )

            items = query_items(
                MUSIC_TABLE,
                key_condition_expression=Key("artist").eq(artist),
                filter_expression=filter_expression,
            )

        return [serialise_music_item(item) for item in items]

    # Case 2: Title-based query using GSI.
    if title:
        filter_expression = build_non_key_filters(
            year=year,
            album=album,
        )

        items = query_items(
            MUSIC_TABLE,
            key_condition_expression=Key("title").eq(title),
            index_name=MUSIC_TITLE_INDEX,
            filter_expression=filter_expression,
        )

        return [serialise_music_item(item) for item in items]

    # Case 3: Controlled Scan fallback for year-only or album-only searches.
    filter_expression = build_non_key_filters(
        year=year,
        album=album,
    )

    items = scan_items(
        MUSIC_TABLE,
        filter_expression=filter_expression,
    )

    return [serialise_music_item(item) for item in items]
