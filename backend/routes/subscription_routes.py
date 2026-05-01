"""
Subscription API routes.

Routes:
- GET /subscriptions?email=...
- POST /subscriptions
- DELETE /subscriptions/<email>/<song_id>
"""

from flask import Blueprint, request

from backend.services.subscription_service import (
    get_user_subscriptions,
    subscribe_to_song,
    remove_subscription,
)
from backend.utils.response import success_response, error_response

subscription_bp = Blueprint("subscriptions", __name__)


def get_json_body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


@subscription_bp.route("/subscriptions", methods=["GET"])
def list_subscriptions():
    email = request.args.get("email", "").strip()

    if not email:
        return error_response(
            message="Missing email",
            status_code=400,
        )

    subscriptions = get_user_subscriptions(email)

    return success_response(
        data=subscriptions,
        message=f"{len(subscriptions)} subscription(s) retrieved",
        status_code=200,
    )


@subscription_bp.route("/subscriptions", methods=["POST"])
def add_subscription():
    data = get_json_body()

    email = str(data.get("email", "")).strip()
    song = data.get("song")

    if not email:
        return error_response(
            message="Missing email",
            status_code=400,
        )

    if not isinstance(song, dict):
        return error_response(
            message="Missing song object",
            status_code=400,
        )

    success, message, response_data = subscribe_to_song(email, song)

    if not success:
        return error_response(
            message=message,
            status_code=409,
        )

    return success_response(
        data=response_data,
        message=message,
        status_code=201,
    )


@subscription_bp.route("/subscriptions/<path:email>/<song_id>", methods=["DELETE"])
def delete_subscription(email, song_id):
    success, message, response_data = remove_subscription(email, song_id)

    if not success:
        return error_response(
            message=message,
            status_code=400,
        )

    return success_response(
        data=response_data,
        message=message,
        status_code=200,
    )
