"""
Authentication API routes.

Routes:
- POST /login
- POST /register
"""

from flask import Blueprint, request

from backend.config import (
    REQUIRED_LOGIN_FIELDS,
    REQUIRED_REGISTER_FIELDS,
)
from backend.services.auth_service import login_user, register_user
from backend.utils.response import (
    success_response,
    error_response,
    validation_error_response,
)

auth_bp = Blueprint("auth", __name__)


def get_json_body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def get_missing_fields(data, required_fields):
    return [field for field in required_fields if not str(data.get(field, "")).strip()]


@auth_bp.route("/login", methods=["POST"])
def login():
    data = get_json_body()

    missing_fields = get_missing_fields(data, REQUIRED_LOGIN_FIELDS)
    if missing_fields:
        return validation_error_response(missing_fields)

    success, message, response_data = login_user(
        email=data.get("email"),
        password=data.get("password"),
    )

    if not success:
        return error_response(message=message, status_code=401)

    return success_response(
        data=response_data,
        message=message,
        status_code=200,
    )


@auth_bp.route("/register", methods=["POST"])
def register():
    data = get_json_body()

    missing_fields = get_missing_fields(data, REQUIRED_REGISTER_FIELDS)
    if missing_fields:
        return validation_error_response(missing_fields)

    success, message, response_data = register_user(
        email=data.get("email"),
        user_name=data.get("user_name"),
        password=data.get("password"),
    )

    if not success:
        return error_response(message=message, status_code=409)

    return success_response(
        data=response_data,
        message=message,
        status_code=201,
    )
