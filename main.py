import importlib
import os
import re
from urllib.parse import urlparse, urlunparse

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Configuration
PLAYLIST_NAME = "Automated Import Playlist"
INPUT_FILE = "songs.txt"
REQUIRED_ENV_VARS = (
    "SPOTIPY_CLIENT_ID",
    "SPOTIPY_CLIENT_SECRET",
    "SPOTIPY_REDIRECT_URI",
)


def get_or_create_playlist(sp, playlist_name, logger):
    """Return an existing current-user playlist by name, or create it if missing."""
    current_user_id = sp.current_user()["id"]
    offset = 0
    limit = 50

    while True:
        page = sp.current_user_playlists(limit=limit, offset=offset)
        items = page.get("items", [])

        for playlist in items:
            if (
                playlist.get("name") == playlist_name
                and playlist.get("owner", {}).get("id") == current_user_id
            ):
                logger.info("Using existing playlist: '{}'", playlist_name)
                return playlist

        if not page.get("next"):
            break

        offset += limit

    logger.info("Creating playlist: '{}'...", playlist_name)
    return sp.current_user_playlist_create(name=playlist_name, public=False)


def normalize_redirect_uri(logger):
    """Replace localhost redirect URIs with loopback IP to avoid deprecation warnings."""
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI", "").strip()
    if not redirect_uri:
        return

    parsed = urlparse(redirect_uri)
    if parsed.hostname != "localhost":
        return

    userinfo = ""
    if parsed.username:
        userinfo = parsed.username
        if parsed.password:
            userinfo = f"{userinfo}:{parsed.password}"
        userinfo = f"{userinfo}@"

    port = f":{parsed.port}" if parsed.port else ""
    updated_netloc = f"{userinfo}127.0.0.1{port}"
    updated_uri = urlunparse(parsed._replace(netloc=updated_netloc))
    os.environ["SPOTIPY_REDIRECT_URI"] = updated_uri
    logger.warning(
        "SPOTIPY_REDIRECT_URI used localhost. Updated to loopback IP: {}", updated_uri
    )


def validate_spotify_env_vars():
    """Fail fast with actionable guidance if Spotify OAuth variables are missing."""
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        missing_vars = ", ".join(missing)
        raise ValueError(
            f"Missing required environment variables: {missing_vars}. "
            "Copy .env.example to .env and set the required SPOTIPY_* values."
        )


def load_environment():
    """Load .env values via python-dotenv and fail with a clear dependency message."""
    try:
        dotenv_module = importlib.import_module("dotenv")
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency 'python-dotenv'. Install it with: pip install python-dotenv"
        ) from exc

    dotenv_module.load_dotenv()


def get_logger():
    """Load loguru logger and fail with clear setup guidance if missing."""
    try:
        loguru_module = importlib.import_module("loguru")
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency 'loguru'. Install it with: pip install loguru"
        ) from exc

    return loguru_module.logger


def clean_song_title(raw_title):
    """
    Sanitizes the input string for better search accuracy.
    Removes text in parentheses/brackets like '(Official Video)'.
    """
    # Remove anything inside () or []
    cleaned = re.sub(r"\(.*?\)|\[.*?\]", "", raw_title)
    # Remove common video descriptors that might not be in brackets
    cleaned = re.sub(
        r"Official Video|Official Music Video|4K|ft\.", "", cleaned, flags=re.IGNORECASE
    )
    return cleaned.strip()


def main():
    logger = get_logger()
    load_environment()
    normalize_redirect_uri(logger)

    try:
        validate_spotify_env_vars()
    except ValueError as exc:
        logger.error("{}", exc)
        return

    # 1. Authenticate with Spotify
    # spotipy automatically looks for the SPOTIPY_* environment variables.
    required_scopes = {
        "playlist-modify-private",
        "playlist-read-private",
    }
    scope = " ".join(sorted(required_scopes))
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    # Force token retrieval so Spotipy can re-authorize when cached scopes are insufficient.
    token_info = sp.auth_manager.get_access_token(as_dict=True, check_cache=True)
    granted_scopes = set((token_info or {}).get("scope", "").split())
    missing_scopes = required_scopes - granted_scopes
    if missing_scopes:
        logger.error(
            "Missing required Spotify scopes: {}. Ensure your Spotify app/user consent includes them and run again.",
            ", ".join(sorted(missing_scopes)),
        )
        return

    # Get current user ID
    user_id = sp.current_user()["id"]
    logger.info("Authenticated as user: {}", user_id)

    # 2. Read and clean the text file
    if not os.path.exists(INPUT_FILE):
        logger.error("{} not found.", INPUT_FILE)
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        raw_lines = [line.strip() for line in file if line.strip()]

    track_uris = []

    # 3. Search and resolve URIs
    logger.info("Resolving tracks...")
    for line in raw_lines:
        search_query = clean_song_title(line)

        # Execute search against the API
        results = sp.search(q=search_query, limit=1, type="track")
        tracks = results.get("tracks", {}).get("items", [])

        if tracks:
            track_uri = tracks[0]["uri"]
            track_uris.append(track_uri)
            logger.success(
                "[FOUND] {} -> {} - {}",
                line,
                tracks[0]["artists"][0]["name"],
                tracks[0]["name"],
            )
        else:
            logger.warning(
                "[FAILED] Could not find: {} (Searched as: {})", line, search_query
            )

    if not track_uris:
        logger.warning("No tracks found. Exiting.")
        return

    # 4. Get or create the Playlist
    try:
        playlist = get_or_create_playlist(sp, PLAYLIST_NAME, logger)
    except spotipy.SpotifyException as exc:
        if exc.http_status == 403:
            logger.error(
                "Spotify denied playlist access/creation (403). Ensure your app has both "
                "'playlist-read-private' and 'playlist-modify-private' granted, then re-authorize "
                "by deleting '.cache' and running again."
            )
            logger.error("Spotify message: {}", str(exc))
            return
        raise

    playlist_id = playlist["id"]

    # 5. Load Tracks into Playlist
    # The API limits adding 100 tracks per request. Spotipy handles this if we pass the whole list,
    # but chunking manually is safer for massive lists to avoid timeout errors.
    chunk_size = 100
    for i in range(0, len(track_uris), chunk_size):
        chunk = track_uris[i : i + chunk_size]
        sp.playlist_add_items(playlist_id, chunk)

    logger.success("Success! Added {} tracks to your new playlist.", len(track_uris))


if __name__ == "__main__":
    main()
