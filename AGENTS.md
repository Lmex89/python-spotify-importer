# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project Overview
- Purpose: Import song titles from a text file, resolve Spotify track URIs, create a private playlist, and add resolved tracks.
- Entry point: `main.py`.
- Sample input list currently present: `songs.txt`.

## Tech Stack
- Python 3
- Spotify Web API via `spotipy`
- Environment loading via `python-dotenv`
- Logging via `loguru`

## Run Commands
- Install dependencies:
  - `pip install -r requirements.txt`
- Run script:
  - `python main.py`

## Environment Setup
- Copy `.env.example` to `.env`.
- Set these values in `.env`:
  - `SPOTIPY_CLIENT_ID`
  - `SPOTIPY_CLIENT_SECRET`
  - `SPOTIPY_REDIRECT_URI`
- Keep `.env` out of version control (already ignored by `.gitignore`).

## Required Environment Variables
Set Spotify OAuth credentials before running:
- `SPOTIPY_CLIENT_ID`
- `SPOTIPY_CLIENT_SECRET`
- `SPOTIPY_REDIRECT_URI`

`spotify_playlist_importer/bootstrap.py` loads `.env` and initialises the logger. `SpotifyOAuth` reads the validated values at auth time.

## Important Repo-Specific Pitfall
- `INPUT_FILE` is configured in `spotify_playlist_importer/config.py` (default: `songs.txt`). Ensure the file exists in the project root.
- If playlist creation returns 403 after successful auth, delete `.cache` to force re-authorization (scopes may be stale).

## Code Conventions For This Repo
- Keep logic in small functions (for example, `clean_song_title` in `input_processing.py`).
- Preserve clear console logging for found/failed track resolution.
- Maintain Spotify API batching limit behavior (100 tracks per add request).
- Use `current_user_playlist_create(...)` — not the deprecated `user_playlist_create(...)`.

## Key Files
- `main.py`: Thin CLI entry point; delegates to the package.
- `songs.txt`: Example song-title input data.
- `spotify_playlist_importer/bootstrap.py`: Logger initialisation and `.env` loading.
- `spotify_playlist_importer/config.py`: Central configuration (`INPUT_FILE`, `PLAYLIST_NAME`, sleep interval).
- `spotify_playlist_importer/input_processing.py`: Input reading and title cleanup.
- `spotify_playlist_importer/spotify_service.py`: Spotify auth, search, and playlist operations.
- `spotify_playlist_importer/app.py`: End-to-end orchestration (`run_import`).

## Agent Scope Note
- Keep changes focused and minimal.
- Do not add unrelated frameworks or tooling to this simple script repository.
