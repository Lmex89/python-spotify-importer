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
- Install dependency:
  - `pip install spotipy python-dotenv loguru`
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

`main.py` loads `.env` first, validates these values, and then `SpotifyOAuth` reads them.

## Important Repo-Specific Pitfall
- Ensure `INPUT_FILE` in `main.py` is set to `songs.txt` and the file exists in the project root.

## Code Conventions For This Repo
- Keep logic in small functions (for example, `clean_song_title`).
- Preserve clear console logging for found/failed track resolution.
- Maintain Spotify API batching limit behavior (100 tracks per add request).

## Key Files
- `main.py`: OAuth, search, playlist creation, and batch add flow.
- `songs.txt`: Example song-title input data.

## Agent Scope Note
- Keep changes focused and minimal.
- Do not add unrelated frameworks or tooling to this simple script repository.
