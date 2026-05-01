"""
Central backend configuration.

This file loads backend constants from environment variables where possible.
It avoids hard-coding deploy-specific values across route and service files.

Real secrets/config values should be stored in .env locally or in the AWS
runtime environment during deployment.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------
# Load .env from project root during local development
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_PATH)


# ---------------------------------------------------------
# AWS Configuration
# ---------------------------------------------------------
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


# ---------------------------------------------------------
# DynamoDB Table Names
# ---------------------------------------------------------
LOGIN_TABLE = os.getenv("LOGIN_TABLE", "login")
MUSIC_TABLE = os.getenv("MUSIC_TABLE", "music")
SUBSCRIPTIONS_TABLE = os.getenv("SUBSCRIPTIONS_TABLE", "subscriptions")


# ---------------------------------------------------------
# DynamoDB Index Names
# ---------------------------------------------------------
MUSIC_TITLE_INDEX = os.getenv("MUSIC_TITLE_INDEX", "title-index")
MUSIC_YEAR_ALBUM_INDEX = os.getenv("MUSIC_YEAR_ALBUM_INDEX", "year-album-index")


# ---------------------------------------------------------
# Flask Backend Settings
# ---------------------------------------------------------
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"


# ---------------------------------------------------------
# CORS Settings
# ---------------------------------------------------------
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")


# ---------------------------------------------------------
# S3 Settings
# These will be used in the next section.
# ---------------------------------------------------------
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "")
S3_IMAGE_PREFIX = os.getenv("S3_IMAGE_PREFIX", "artist-images/")


# ---------------------------------------------------------
# Application Constants
# ---------------------------------------------------------
REQUIRED_SONG_FIELDS = ["title", "artist", "year", "album"]
REQUIRED_REGISTER_FIELDS = ["email", "user_name", "password"]
REQUIRED_LOGIN_FIELDS = ["email", "password"]

DEFAULT_PAGE_LIMIT = 50
MAX_PAGE_LIMIT = 100

ERROR_INVALID_LOGIN = "email or password is invalid"
ERROR_EMAIL_EXISTS = "The email already exists"
ERROR_NO_QUERY_FIELDS = "At least one query field must be provided"
ERROR_NO_RESULTS = "No result is retrieved. Please query again"
ERROR_MISSING_FIELDS = "Missing required field(s)"
MESSAGE_REGISTER_SUCCESS = "Registration successful"
MESSAGE_LOGIN_SUCCESS = "Login successful"
MESSAGE_SUBSCRIBE_SUCCESS = "Song subscribed successfully"
MESSAGE_REMOVE_SUCCESS = "Song removed successfully"
