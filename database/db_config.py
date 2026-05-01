from pathlib import Path

# ---------------------------------------------------------
# AWS Configuration
# ---------------------------------------------------------
# Change this only if your AWS Academy lab uses a different region.
AWS_REGION = "us-east-1"

# ---------------------------------------------------------
# DynamoDB Table Names
# ---------------------------------------------------------
LOGIN_TABLE = "login"
MUSIC_TABLE = "music"
SUBSCRIPTIONS_TABLE = "subscriptions"

# ---------------------------------------------------------
# DynamoDB Index Names
# ---------------------------------------------------------
MUSIC_TITLE_INDEX = "title-index"
MUSIC_YEAR_ALBUM_INDEX = "year-album-index"

# ---------------------------------------------------------
# Project Paths
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
SONGS_JSON_PATH = DATA_DIR / "2026a2_songs.json"


# ---------------------------------------------------------
# Key Construction Helpers
# ---------------------------------------------------------
def clean_key_part(value: str) -> str:
    """
    Converts a value into a safe string component for DynamoDB sort keys.
    Keeps the original meaning while removing leading/trailing spaces.
    """
    if value is None:
        return ""
    return str(value).strip()


def build_music_sort_key(title: str, year: str, album: str) -> str:
    """
    Sort key for the music table.
    Used with artist as the partition key.
    """
    title_part = clean_key_part(title)
    year_part = clean_key_part(year)
    album_part = clean_key_part(album)
    return f"{title_part}#{year_part}#{album_part}"


def build_title_index_sort_key(artist: str, year: str, album: str) -> str:
    """
    Sort key for the title GSI.
    Used with title as the GSI partition key.
    """
    artist_part = clean_key_part(artist)
    year_part = clean_key_part(year)
    album_part = clean_key_part(album)
    return f"{artist_part}#{year_part}#{album_part}"


def build_year_album_lsi_sort_key(year: str, album: str, title: str) -> str:
    """
    Sort key for the music table LSI.
    Used with artist as the partition key.
    """
    year_part = clean_key_part(year)
    album_part = clean_key_part(album)
    title_part = clean_key_part(title)
    return f"{year_part}#{album_part}#{title_part}"


def build_song_id(title: str, artist: str, year: str, album: str) -> str:
    """
    Creates a stable unique song identifier from all natural identifying fields.
    This prevents different versions of the same title from overwriting each other.
    """
    import hashlib

    raw_key = "|".join(
        [
            clean_key_part(title).lower(),
            clean_key_part(artist).lower(),
            clean_key_part(year).lower(),
            clean_key_part(album).lower(),
        ]
    )
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]
