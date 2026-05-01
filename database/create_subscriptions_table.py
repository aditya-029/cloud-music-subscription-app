"""
Create the DynamoDB subscriptions table.

Run from project root:
    python -m database.create_subscriptions_table

Purpose:
- Stores each user's subscribed songs.
- Allows efficient retrieval of all subscriptions for one logged-in user.
- Allows deletion of one specific subscribed song.
"""

import boto3
from botocore.exceptions import ClientError

from database.db_config import AWS_REGION, SUBSCRIPTIONS_TABLE


def create_subscriptions_table():
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

    try:
        table = dynamodb.Table(SUBSCRIPTIONS_TABLE)
        table.load()
        print(f"Table already exists: {SUBSCRIPTIONS_TABLE}")
        return
    except ClientError as error:
        if error.response["Error"]["Code"] != "ResourceNotFoundException":
            raise

    table = dynamodb.create_table(
        TableName=SUBSCRIPTIONS_TABLE,
        KeySchema=[
            {"AttributeName": "email", "KeyType": "HASH"},
            {"AttributeName": "song_id", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "email", "AttributeType": "S"},
            {"AttributeName": "song_id", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    table.wait_until_exists()

    print(f"Created table: {SUBSCRIPTIONS_TABLE}")
    print("Primary key: email + song_id")
    print("Billing mode: PAY_PER_REQUEST")


if __name__ == "__main__":
    create_subscriptions_table()
