"""Spotify API service helpers."""

import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from .config import PLAYLIST_ADD_CHUNK_SIZE, PLAYLIST_PAGE_LIMIT
from .input_processing import clean_song_title


def authenticate_spotify(required_scopes):
    """Create an authenticated Spotipy client and validate granted scopes."""
    scope = " ".join(sorted(required_scopes))
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    token_info = sp.auth_manager.get_cached_token()
    if not token_info:
        sp.auth_manager.get_access_token(check_cache=False)
        token_info = sp.auth_manager.get_cached_token()

    granted_scopes = set((token_info or {}).get("scope", "").split())
    missing_scopes = required_scopes - granted_scopes
    if missing_scopes:
        missing = ", ".join(sorted(missing_scopes))
        raise ValueError(
            f"Missing required Spotify scopes: {missing}. "
            "Ensure your Spotify app/user consent includes them and run again."
        )

    return sp


def get_or_create_playlist(sp, playlist_name, logger, limit=PLAYLIST_PAGE_LIMIT):
    """Return an existing current-user playlist by name, or create it if missing."""
    current_user_id = sp.current_user()["id"]
    offset = 0

    while True:
        page = sp.current_user_playlists(limit=limit, offset=offset)
        items = page.get("items", [])

        for playlist in items:
            if (
                playlist.get("name") == playlist_name
                and playlist.get("owner", {}).get("id") == current_user_id
            ):
                logger.info(f"Using existing playlist: '{playlist_name}'")
                return playlist

        if not page.get("next"):
            break

        offset += limit

    logger.info(f"Creating playlist: '{playlist_name}'...")
    return sp.current_user_playlist_create(name=playlist_name, public=False)


def resolve_track_uris(sp, raw_lines, logger, api_call_sleep_seconds):
    """Resolve user-provided song titles into Spotify track URIs."""
    track_uris = []

    logger.info("Resolving tracks...")
    for line in raw_lines:
        search_query = clean_song_title(line)
        results = sp.search(q=search_query, limit=1, type="track")
        if api_call_sleep_seconds > 0:
            time.sleep(api_call_sleep_seconds)
        tracks = results.get("tracks", {}).get("items", [])

        if tracks:
            track_uri = tracks[0]["uri"]
            track_uris.append(track_uri)
            logger.success(
                f"[FOUND] {line} -> {tracks[0]['artists'][0]['name']} - {tracks[0]['name']}"
            )
        else:
            logger.warning(f"[FAILED] Could not find: {line} (Searched as: {search_query})")

    return track_uris


def add_tracks_to_playlist(
    sp,
    playlist_id,
    track_uris,
    api_call_sleep_seconds,
    chunk_size=PLAYLIST_ADD_CHUNK_SIZE,
):
    """Add tracks to a playlist in chunked requests."""
    for i in range(0, len(track_uris), chunk_size):
        chunk = track_uris[i : i + chunk_size]
        sp.playlist_add_items(playlist_id, chunk)
        if api_call_sleep_seconds > 0:
            time.sleep(api_call_sleep_seconds)
