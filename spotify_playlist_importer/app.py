"""Application orchestration for Spotify import flow."""

import os
from http import HTTPStatus

import spotipy

from .bootstrap import get_logger, load_environment, normalize_redirect_uri
from .config import (
    INPUT_FILE,
    PLAYLIST_NAME,
    REQUIRED_SCOPES,
    get_api_call_sleep_seconds,
    validate_spotify_env_vars,
)
from .input_processing import read_song_lines
from .spotify_service import (
    add_tracks_to_playlist,
    authenticate_spotify,
    get_or_create_playlist,
    resolve_track_uris,
)


def run_import() -> None:
    """Run the song import workflow end-to-end."""
    logger = get_logger()
    load_environment()
    normalize_redirect_uri(logger)

    try:
        validate_spotify_env_vars()
    except ValueError as exc:
        logger.error(f"{exc}")
        return

    try:
        sp = authenticate_spotify(REQUIRED_SCOPES)
    except ValueError as exc:
        logger.error(f"{exc}")
        return

    user_id = sp.current_user()["id"]
    logger.info(f"Authenticated as user: {user_id}")

    if not os.path.exists(INPUT_FILE):
        logger.error(f"{INPUT_FILE} not found.")
        return

    raw_lines = read_song_lines(INPUT_FILE)
    api_call_sleep_seconds = get_api_call_sleep_seconds()
    track_uris = resolve_track_uris(sp, raw_lines, logger, api_call_sleep_seconds)

    if not track_uris:
        logger.warning("No tracks found. Exiting.")
        return

    try:
        playlist = get_or_create_playlist(sp, PLAYLIST_NAME, logger)
    except spotipy.SpotifyException as exc:
        if exc.http_status == HTTPStatus.FORBIDDEN:
            logger.error(
                "Spotify denied playlist access/creation (403). Ensure your app has both "
                "'playlist-read-private' and 'playlist-modify-private' granted, then re-authorize "
                "by deleting '.cache' and running again."
            )
            logger.error(f"Spotify message: {exc}")
            return
        raise

    add_tracks_to_playlist(
        sp,
        playlist["id"],
        track_uris,
        api_call_sleep_seconds,
    )
    logger.success(f"Success! Added {len(track_uris)} tracks to your new playlist.")
