"""
Music API routes.

Routes:
- GET /songs
"""

from flask import Blueprint, request

from backend.config import (
    ERROR_NO_QUERY_FIELDS,
    ERROR_NO_RESULTS,
)
from backend.services.music_service import search_music
from backend.utils.response import success_response, error_response

music_bp = Blueprint("music", __name__)


@music_bp.route("/songs", methods=["GET"])
def get_songs():
    title = request.args.get("title", "").strip()
    artist = request.args.get("artist", "").strip()
    year = request.args.get("year", "").strip()
    album = request.args.get("album", "").strip()

    if not any([title, artist, year, album]):
        return error_response(
            message=ERROR_NO_QUERY_FIELDS,
            status_code=400,
        )

    results = search_music(
        title=title,
        artist=artist,
        year=year,
        album=album,
    )

    if not results:
        return success_response(
            data=[],
            message=ERROR_NO_RESULTS,
            status_code=200,
        )

    return success_response(
        data=results,
        message=f"{len(results)} result(s) retrieved",
        status_code=200,
    )
