"""
Create the DynamoDB login table.

Run from project root:
    python -m database.create_login_table
"""

import boto3
from botocore.exceptions import ClientError

from database.db_config import AWS_REGION, LOGIN_TABLE


def create_login_table():
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

    try:
        table = dynamodb.Table(LOGIN_TABLE)
        table.load()
        print(f"Table already exists: {LOGIN_TABLE}")
        return
    except ClientError as error:
        if error.response["Error"]["Code"] != "ResourceNotFoundException":
            raise

    table = dynamodb.create_table(
        TableName=LOGIN_TABLE,
        KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    table.wait_until_exists()

    print(f"Created table: {LOGIN_TABLE}")
    print("Primary key: email")
    print("Billing mode: PAY_PER_REQUEST")


if __name__ == "__main__":
    create_login_table()
