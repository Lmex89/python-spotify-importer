# Spotify Playlist Creator

A Python script that imports song titles from a text file, resolves them to Spotify track URIs, creates a private playlist, and adds the resolved tracks.

## Prerequisites

- Python 3
- Spotify Developer Account (for API credentials)

## Installation

1. Install dependencies:
```bash
pip install spotipy python-dotenv loguru
```

2. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your Spotify API credentials to `.env`:
     ```
     SPOTIPY_CLIENT_ID=your_client_id
     SPOTIPY_CLIENT_SECRET=your_client_secret
     SPOTIPY_REDIRECT_URI=your_redirect_uri
     ```

## Usage

1. Prepare your input file with song titles (one per line). The script expects `songs.txt` by default.
   - Note: If using `list.txt`, update `INPUT_FILE` in `main.py`

2. Run the script:
```bash
python main.py
```

The script will:
- Authenticate with Spotify
- Search for each song title
- Create a private playlist
- Add resolved tracks in batches (up to 100 per request)
- Display found/failed track resolutions in the console

## Configuration

Edit `main.py` to change:
- `INPUT_FILE`: Path to your input song list
- Playlist name and description
- Other Spotify API parameters

## Notes

- Keep `.env` out of version control (already configured in `.gitignore`)
- The script respects Spotify API batching limits (100 tracks per add request)
- Console logging shows detailed progress for debugging

## Tech Stack

- **spotipy**: Spotify Web API client
- **python-dotenv**: Environment variable management
- **loguru**: Advanced logging
