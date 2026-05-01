"""
S3 service.

Creates secure temporary image URLs for frontend display.
The bucket does not need to be public when presigned URLs are used.
"""

import boto3

from backend.config import AWS_REGION, S3_BUCKET_NAME

PRESIGNED_URL_EXPIRY_SECONDS = 3600


def get_s3_client():
    return boto3.client("s3", region_name=AWS_REGION)


def generate_presigned_image_url(s3_image_key):
    """
    Returns a temporary presigned S3 URL for an artist image.

    If no S3 key is available, returns an empty string so the frontend
    can fall back to img_url if needed.
    """
    if not s3_image_key:
        return ""

    if not S3_BUCKET_NAME:
        return ""

    s3_client = get_s3_client()

    return s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": S3_BUCKET_NAME,
            "Key": s3_image_key,
        },
        ExpiresIn=PRESIGNED_URL_EXPIRY_SECONDS,
    )
