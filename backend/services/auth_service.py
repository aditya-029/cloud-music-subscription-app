"""
Authentication service.

Handles user login, email uniqueness checks, and user registration.
This file contains business logic only. Flask routes should call these
functions instead of directly accessing DynamoDB.
"""

from botocore.exceptions import ClientError

from backend.config import (
    LOGIN_TABLE,
    ERROR_INVALID_LOGIN,
    ERROR_EMAIL_EXISTS,
    MESSAGE_LOGIN_SUCCESS,
    MESSAGE_REGISTER_SUCCESS,
)
from backend.services.dynamodb_service import get_item, put_item


def get_user_by_email(email):
    """
    Returns a user record by email, or None if the user does not exist.
    """
    if not email:
        return None

    return get_item(LOGIN_TABLE, {"email": email.strip()})


def login_user(email, password):
    """
    Validates user login credentials.

    Returns:
        (success: bool, message: str, data: dict | None)
    """
    email = str(email or "").strip()
    password = str(password or "").strip()

    if not email or not password:
        return False, ERROR_INVALID_LOGIN, None

    user = get_user_by_email(email)

    if not user:
        return False, ERROR_INVALID_LOGIN, None

    if user.get("password") != password:
        return False, ERROR_INVALID_LOGIN, None

    return (
        True,
        MESSAGE_LOGIN_SUCCESS,
        {
            "email": user["email"],
            "user_name": user["user_name"],
        },
    )


def register_user(email, user_name, password):
    """
    Registers a new user if the email does not already exist.

    Returns:
        (success: bool, message: str, data: dict | None)
    """
    email = str(email or "").strip()
    user_name = str(user_name or "").strip()
    password = str(password or "").strip()

    existing_user = get_user_by_email(email)

    if existing_user:
        return False, ERROR_EMAIL_EXISTS, None

    item = {
        "email": email,
        "user_name": user_name,
        "password": password,
    }

    try:
        put_item(
            LOGIN_TABLE,
            item,
            condition_expression="attribute_not_exists(email)",
        )
    except ClientError as error:
        if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False, ERROR_EMAIL_EXISTS, None
        raise

    return (
        True,
        MESSAGE_REGISTER_SUCCESS,
        {
            "email": email,
            "user_name": user_name,
        },
    )
