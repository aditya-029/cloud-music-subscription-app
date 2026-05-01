"""
Verify DynamoDB tables and key query patterns.

Run from project root:
    python -m database.verify_database

This script checks:
- login table has the required default users
- music table contains all 137 songs
- subscriptions table exists
- artist queries work
- artist + year filtering works
- artist + album filtering works
- title-index GSI works
"""

import boto3
from boto3.dynamodb.conditions import Key, Attr

from database.db_config import (
    AWS_REGION,
    LOGIN_TABLE,
    MUSIC_TABLE,
    SUBSCRIPTIONS_TABLE,
    MUSIC_TITLE_INDEX,
    MUSIC_YEAR_ALBUM_INDEX,
)

EXPECTED_LOGIN_USERS = 10
EXPECTED_MUSIC_RECORDS = 137


def get_table(table_name):
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    return dynamodb.Table(table_name)


def count_table_items(table):
    response = table.scan(Select="COUNT")
    return response["Count"]


def verify_table_exists(table_name):
    table = get_table(table_name)
    table.load()
    print(f"Table exists: {table_name}")
    return table


def verify_login_table():
    print("\nVerifying login table...")
    table = verify_table_exists(LOGIN_TABLE)

    count = count_table_items(table)
    print(f"Login users found: {count}")

    if count < EXPECTED_LOGIN_USERS:
        raise AssertionError(
            f"Expected at least {EXPECTED_LOGIN_USERS} login users, found {count}"
        )

    response = table.get_item(Key={"email": "s40978850@student.rmit.edu.au"})

    if "Item" not in response:
        raise AssertionError("Default test user was not found in login table.")

    item = response["Item"]
    print("Sample login user found: " f"{item['email']} / {item['user_name']}")


def verify_music_table_count():
    print("\nVerifying music table count...")
    table = verify_table_exists(MUSIC_TABLE)

    count = count_table_items(table)
    print(f"Music records found: {count}")

    if count != EXPECTED_MUSIC_RECORDS:
        raise AssertionError(
            f"Expected {EXPECTED_MUSIC_RECORDS} music records, found {count}"
        )


def verify_subscriptions_table():
    print("\nVerifying subscriptions table...")
    verify_table_exists(SUBSCRIPTIONS_TABLE)
    print("Subscriptions table is ready.")


def verify_artist_query():
    print("\nTesting artist query: Taylor Swift...")
    table = get_table(MUSIC_TABLE)

    response = table.query(KeyConditionExpression=Key("artist").eq("Taylor Swift"))

    items = response.get("Items", [])
    print(f"Taylor Swift records found: {len(items)}")

    if len(items) != 8:
        raise AssertionError(f"Expected 8 Taylor Swift records, found {len(items)}")


def verify_artist_year_query():
    print("\nTesting artist + year query using LSI: Jimmy Buffett, 1974...")
    table = get_table(MUSIC_TABLE)

    response = table.query(
        IndexName=MUSIC_YEAR_ALBUM_INDEX,
        KeyConditionExpression=Key("artist").eq("Jimmy Buffett")
        & Key("year_album_title").begins_with("1974#"),
    )

    items = response.get("Items", [])
    print(f"Jimmy Buffett 1974 records found: {len(items)}")

    if len(items) != 3:
        raise AssertionError(
            f"Expected 3 Jimmy Buffett 1974 records, found {len(items)}"
        )


def verify_artist_album_query():
    print("\nTesting artist + album query: Taylor Swift, Fearless...")
    table = get_table(MUSIC_TABLE)

    response = table.query(
        KeyConditionExpression=Key("artist").eq("Taylor Swift"),
        FilterExpression=Attr("album").eq("Fearless"),
    )

    items = response.get("Items", [])
    print(f"Taylor Swift Fearless records found: {len(items)}")

    if len(items) != 2:
        raise AssertionError(
            f"Expected 2 Taylor Swift Fearless records, found {len(items)}"
        )


def verify_title_gsi_query():
    print("\nTesting title-index GSI query: Bad Blood...")
    table = get_table(MUSIC_TABLE)

    response = table.query(
        IndexName=MUSIC_TITLE_INDEX,
        KeyConditionExpression=Key("title").eq("Bad Blood"),
    )

    items = response.get("Items", [])
    print(f"Bad Blood records found: {len(items)}")

    if len(items) != 2:
        raise AssertionError(f"Expected 2 Bad Blood records, found {len(items)}")


def verify_scan_operation():
    print("\nTesting controlled Scan operation: year = 2021...")
    table = get_table(MUSIC_TABLE)

    response = table.scan(FilterExpression=Attr("year").eq("2021"))

    items = response.get("Items", [])
    print(f"2021 records found using Scan: {len(items)}")

    if len(items) != 1:
        raise AssertionError(f"Expected 1 record from 2021, found {len(items)}")


def main():
    print("=" * 70)
    print("DATABASE VERIFICATION")
    print("=" * 70)

    verify_login_table()
    verify_music_table_count()
    verify_subscriptions_table()

    verify_artist_query()
    verify_artist_year_query()
    verify_artist_album_query()
    verify_title_gsi_query()
    verify_scan_operation()

    print("\n" + "=" * 70)
    print("All database checks passed.")
    print("Section 1 DynamoDB setup is complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
