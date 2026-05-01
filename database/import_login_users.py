"""
Import the 10 required default users into the DynamoDB login table.

Run from project root:
    python -m database.import_login_users
"""

import boto3

from database.db_config import AWS_REGION, LOGIN_TABLE

BASE_STUDENT_ID = "s4097885"
USERNAME_BASE = "AdityaRajbhoj"


def build_default_users():
    users = []

    for i in range(10):
        users.append(
            {
                "email": f"{BASE_STUDENT_ID}{i}@student.rmit.edu.au",
                "user_name": f"{USERNAME_BASE}{i}",
                "password": (
                    f"{i}01234" if i == 9 else f"{i}{i + 1}{i + 2}{i + 3}{i + 4}{i + 5}"
                ),
            }
        )

    return users


def import_login_users():
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    table = dynamodb.Table(LOGIN_TABLE)

    users = build_default_users()

    for user in users:
        table.put_item(
            Item=user,
            ConditionExpression="attribute_not_exists(email)",
        )
        print(f"Inserted user: {user['email']}")

    print(f"\nImported {len(users)} users into table: {LOGIN_TABLE}")


if __name__ == "__main__":
    import_login_users()
