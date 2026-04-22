"""Configuration and environment validation helpers."""

import os

PLAYLIST_NAME = " Coded Automated Import Playlist"
INPUT_FILE = "songs.txt"
REQUIRED_ENV_VARS = (
    "SPOTIPY_CLIENT_ID",
    "SPOTIPY_CLIENT_SECRET",
    "SPOTIPY_REDIRECT_URI",
)
PLAYLIST_PAGE_LIMIT = 50
PLAYLIST_ADD_CHUNK_SIZE = 100


def get_api_call_sleep_seconds():
    """Read API sleep interval from environment."""
    return float(os.getenv("SPOTIPY_API_SLEEP_SECONDS", "1.0"))


def validate_spotify_env_vars():
    """Fail fast with actionable guidance if Spotify OAuth variables are missing."""
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        missing_vars = ", ".join(missing)
        raise ValueError(
            f"Missing required environment variables: {missing_vars}. "
            "Copy .env.example to .env and set the required SPOTIPY_* values."
        )
