"""
Create the DynamoDB music table.

Run from project root:
    python -m database.create_music_table

HD design purpose:
- Preserves all 137 song records without overwriting duplicate titles.
- Supports artist-based marker queries efficiently.
- Includes one purposeful GSI for title-based lookup.
- Includes one purposeful LSI for artist + year/album filtering.
"""

import boto3
from botocore.exceptions import ClientError

from database.db_config import (
    AWS_REGION,
    MUSIC_TABLE,
    MUSIC_TITLE_INDEX,
    MUSIC_YEAR_ALBUM_INDEX,
)


def create_music_table():
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

    try:
        table = dynamodb.Table(MUSIC_TABLE)
        table.load()
        print(f"Table already exists: {MUSIC_TABLE}")
        return
    except ClientError as error:
        if error.response["Error"]["Code"] != "ResourceNotFoundException":
            raise

    table = dynamodb.create_table(
        TableName=MUSIC_TABLE,
        KeySchema=[
            {"AttributeName": "artist", "KeyType": "HASH"},
            {"AttributeName": "title_year_album", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "artist", "AttributeType": "S"},
            {"AttributeName": "title_year_album", "AttributeType": "S"},
            {"AttributeName": "title", "AttributeType": "S"},
            {"AttributeName": "artist_year_album", "AttributeType": "S"},
            {"AttributeName": "year_album_title", "AttributeType": "S"},
        ],
        LocalSecondaryIndexes=[
            {
                "IndexName": MUSIC_YEAR_ALBUM_INDEX,
                "KeySchema": [
                    {"AttributeName": "artist", "KeyType": "HASH"},
                    {"AttributeName": "year_album_title", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": MUSIC_TITLE_INDEX,
                "KeySchema": [
                    {"AttributeName": "title", "KeyType": "HASH"},
                    {"AttributeName": "artist_year_album", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    table.wait_until_exists()

    print(f"Created table: {MUSIC_TABLE}")
    print("Primary key: artist + title_year_album")
    print(f"GSI: {MUSIC_TITLE_INDEX} using title + artist_year_album")
    print(f"LSI: {MUSIC_YEAR_ALBUM_INDEX} using artist + year_album_title")
    print("Billing mode: PAY_PER_REQUEST")


if __name__ == "__main__":
    create_music_table()
