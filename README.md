# Spotify Playlist Creator

A Python script that imports song titles from a text file, resolves them to Spotify track URIs, creates a private playlist, and adds the resolved tracks.

## Prerequisites

- Python 3
- Spotify Developer Account (for API credentials)

## Installation

1. (Optional but recommended) Create and activate a virtual environment:
```bash
python3 -m venv .venv_script
source .venv_script/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your Spotify API credentials to `.env`:
     ```
     SPOTIPY_CLIENT_ID=your_client_id
     SPOTIPY_CLIENT_SECRET=your_client_secret
     SPOTIPY_REDIRECT_URI=your_redirect_uri
     ```

## Usage

1. If you are using a virtual environment, activate it:
```bash
source .venv_script/bin/activate
```

2. Prepare your input file with song titles (one per line). The script expects `songs.txt` by default.

3. Run the script:
```bash
python main.py
```

The script delegates to the package workflow in `spotify_playlist_importer/app.py`.

The script will:
- Authenticate with Spotify
- Search for each song title
- Create a private playlist
- Add resolved tracks in batches (up to 100 per request)
- Display found/failed track resolutions in the console

## Configuration

Edit `spotify_playlist_importer/config.py` to change:
- `INPUT_FILE`: Path to your input song list
- `PLAYLIST_NAME`: Playlist title

Runtime pacing can be adjusted with environment variable:
- `SPOTIPY_API_SLEEP_SECONDS` (default: `1.0`)

Core responsibilities are split across modules:
- `spotify_playlist_importer/bootstrap.py`: logger and `.env` loading/bootstrap
- `spotify_playlist_importer/input_processing.py`: input reading and title cleanup
- `spotify_playlist_importer/spotify_service.py`: Spotify auth, search, playlist operations
- `spotify_playlist_importer/app.py`: end-to-end orchestration

## Notes

- Keep `.env` out of version control (already configured in `.gitignore`)
- The script respects Spotify API batching limits (100 tracks per add request)
- Console logging shows detailed progress for debugging

## Tech Stack

- **spotipy**: Spotify Web API client
- **python-dotenv**: Environment variable management
- **loguru**: Advanced logging
