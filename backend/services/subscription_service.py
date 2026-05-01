"""
Subscription service.

Handles user subscription operations:
- list subscribed songs
- subscribe to a song
- remove a subscribed song
"""

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

from backend.config import (
    SUBSCRIPTIONS_TABLE,
    MESSAGE_SUBSCRIBE_SUCCESS,
    MESSAGE_REMOVE_SUCCESS,
)
from backend.services.dynamodb_service import (
    get_subscriptions_table,
    put_item,
    delete_item,
)
from backend.services.s3_service import generate_presigned_image_url


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def serialise_subscription_item(item):
    """
    Converts a DynamoDB subscription item into a frontend-friendly object.

    image_url is the URL the frontend should use for display.
    It prefers a secure temporary S3 presigned URL and falls back to the
    original dataset img_url if an S3 key is unavailable.
    """
    s3_image_key = item.get("s3_image_key", "")

    return {
        "email": item.get("email"),
        "song_id": item.get("song_id"),
        "title": item.get("title"),
        "artist": item.get("artist"),
        "year": item.get("year"),
        "album": item.get("album"),
        "img_url": item.get("img_url"),
        "s3_image_key": s3_image_key,
        "image_url": generate_presigned_image_url(s3_image_key) or item.get("img_url"),
    }


def get_user_subscriptions(email):
    """
    Returns all songs subscribed by one user.
    """
    email = clean(email)

    if not email:
        return []

    table = get_subscriptions_table()

    response = table.query(KeyConditionExpression=Key("email").eq(email))

    items = response.get("Items", [])
    return [serialise_subscription_item(item) for item in items]


def subscribe_to_song(email, song):
    """
    Adds a song to a user's subscription list.

    The frontend/backend should provide the selected song object from search results.
    Duplicate subscriptions are prevented by email + song_id.
    """
    email = clean(email)

    item = {
        "email": email,
        "song_id": clean(song.get("song_id")),
        "title": clean(song.get("title")),
        "artist": clean(song.get("artist")),
        "year": clean(song.get("year")),
        "album": clean(song.get("album")),
        "img_url": clean(song.get("img_url")),
        "s3_image_key": clean(song.get("s3_image_key")),
    }

    if not item["email"] or not item["song_id"]:
        return False, "Missing email or song_id", None

    try:
        put_item(
            SUBSCRIPTIONS_TABLE,
            item,
            condition_expression=(
                "attribute_not_exists(email) " "AND attribute_not_exists(song_id)"
            ),
        )
    except ClientError as error:
        if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False, "Song is already subscribed", None
        raise

    return True, MESSAGE_SUBSCRIBE_SUCCESS, serialise_subscription_item(item)


def remove_subscription(email, song_id):
    """
    Removes one subscribed song for a user.
    """
    email = clean(email)
    song_id = clean(song_id)

    if not email or not song_id:
        return False, "Missing email or song_id", None

    delete_item(
        SUBSCRIPTIONS_TABLE,
        {
            "email": email,
            "song_id": song_id,
        },
    )

    return (
        True,
        MESSAGE_REMOVE_SUCCESS,
        {
            "email": email,
            "song_id": song_id,
        },
    )
