"""
Native AWS Lambda backend for the Cloud Music Subscription App.

This file implements the required API Gateway + Lambda backend routes
without depending on Flask/Wsgi translation. It reuses the same backend
service logic used by the EC2 and ECS deployments.

Supported routes:
- GET    /health
- POST   /login
- POST   /register
- GET    /songs
- GET    /subscriptions
- POST   /subscriptions
- DELETE /subscriptions/{email}/{song_id}
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional
from urllib.parse import unquote

from backend.services.auth_service import login_user, register_user
from backend.services.music_service import search_music
from backend.services.subscription_service import (
    get_user_subscriptions,
    subscribe_to_song,
    remove_subscription,
)


def response(
    status_code: int,
    success: bool,
    message: str,
    data: Any = None,
) -> Dict[str, Any]:
    """
    Creates a consistent API Gateway-compatible JSON response.
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,DELETE,OPTIONS",
        },
        "body": json.dumps(
            {
                "success": success,
                "message": message,
                "data": data,
            },
            default=str,
        ),
    }


def parse_body(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safely parses a JSON request body.
    """
    body = event.get("body")

    if not body:
        return {}

    if isinstance(body, dict):
        return body

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {}


def get_method(event: Dict[str, Any]) -> str:
    """
    Supports both API Gateway REST API payload v1 and HTTP API payload v2.
    """
    if "httpMethod" in event:
        return event.get("httpMethod", "GET").upper()

    return event.get("requestContext", {}).get("http", {}).get("method", "GET").upper()


def get_path(event: Dict[str, Any]) -> str:
    """
    Supports both API Gateway REST API payload v1 and HTTP API payload v2.
    """
    path = event.get("path") or event.get("rawPath") or "/"

    if not path.startswith("/"):
        path = f"/{path}"

    return path.rstrip("/") if path != "/" else path


def get_query_params(event: Dict[str, Any]) -> Dict[str, str]:
    """
    Returns query string parameters safely.
    """
    params = event.get("queryStringParameters") or {}
    return {key: value for key, value in params.items() if value is not None}


def get_path_param(
    event: Dict[str, Any],
    param_name: str,
    fallback_index: Optional[int] = None,
) -> str:
    """
    Gets a path parameter from API Gateway if available.
    Falls back to extracting from the URL path when testing with proxy routes.
    """
    path_params = event.get("pathParameters") or {}

    if param_name in path_params and path_params[param_name] is not None:
        return unquote(str(path_params[param_name]))

    if fallback_index is not None:
        parts = [part for part in get_path(event).split("/") if part]
        if len(parts) > fallback_index:
            return unquote(parts[fallback_index])

    return ""


def handle_options() -> Dict[str, Any]:
    """
    Handles browser CORS preflight requests.
    """
    return response(200, True, "CORS preflight successful", None)


def handle_health() -> Dict[str, Any]:
    return response(
        200,
        True,
        "Backend is running",
        {"status": "healthy"},
    )


def handle_login(event: Dict[str, Any]) -> Dict[str, Any]:
    body = parse_body(event)

    email = str(body.get("email", "")).strip()
    password = str(body.get("password", "")).strip()

    success, message, data = login_user(email, password)

    return response(
        200 if success else 401,
        success,
        message,
        data,
    )


def handle_register(event: Dict[str, Any]) -> Dict[str, Any]:
    body = parse_body(event)

    email = str(body.get("email", "")).strip()
    user_name = str(
        body.get("user_name") or body.get("username") or body.get("name") or ""
    ).strip()
    password = str(body.get("password", "")).strip()

    success, message, data = register_user(email, user_name, password)

    return response(
        201 if success else 400,
        success,
        message,
        data,
    )


def handle_song_search(event: Dict[str, Any]) -> Dict[str, Any]:
    params = get_query_params(event)

    title = params.get("title", "")
    artist = params.get("artist", "")
    year = params.get("year", "")
    album = params.get("album", "")

    results = search_music(
        title=title,
        artist=artist,
        year=year,
        album=album,
    )

    return response(
        200,
        True,
        f"{len(results)} result(s) retrieved",
        results,
    )


def handle_get_subscriptions(event: Dict[str, Any]) -> Dict[str, Any]:
    params = get_query_params(event)
    email = str(params.get("email", "")).strip()

    subscriptions = get_user_subscriptions(email)

    return response(
        200,
        True,
        f"{len(subscriptions)} subscription(s) retrieved",
        subscriptions,
    )


def handle_subscribe(event: Dict[str, Any]) -> Dict[str, Any]:
    body = parse_body(event)

    email = str(body.get("email", "")).strip()
    song = body.get("song") or {}

    success, message, data = subscribe_to_song(email, song)

    status_code = 201 if success else 400

    if message == "Song is already subscribed":
        status_code = 409

    return response(
        status_code,
        success,
        message,
        data,
    )


def handle_remove_subscription(event: Dict[str, Any]) -> Dict[str, Any]:
    email = get_path_param(event, "email", fallback_index=1)
    song_id = get_path_param(event, "song_id", fallback_index=2)

    success, message, data = remove_subscription(email, song_id)

    return response(
        200 if success else 400,
        success,
        message,
        data,
    )


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for API Gateway.
    """
    method = get_method(event)
    path = get_path(event)

    try:
        if method == "OPTIONS":
            return handle_options()

        if method == "GET" and path == "/health":
            return handle_health()

        if method == "POST" and path == "/login":
            return handle_login(event)

        if method == "POST" and path == "/register":
            return handle_register(event)

        if method == "GET" and path == "/songs":
            return handle_song_search(event)

        if method == "GET" and path == "/subscriptions":
            return handle_get_subscriptions(event)

        if method == "POST" and path == "/subscriptions":
            return handle_subscribe(event)

        if method == "DELETE" and path.startswith("/subscriptions/"):
            return handle_remove_subscription(event)

        return response(
            404,
            False,
            f"Route not found: {method} {path}",
            None,
        )

    except Exception as error:
        return response(
            500,
            False,
            "Internal server error",
            {"error": str(error)},
        )
