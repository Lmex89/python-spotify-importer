"""CLI entry point for the Spotify playlist importer."""

from spotify_playlist_importer import run_import
from spotify_playlist_importer.bootstrap import get_logger


def main() -> None:
    """Run the Spotify importer workflow with top-level logging."""
    logger = get_logger()
    logger.info("Starting Spotify playlist import.")
    run_import()
    logger.info("Spotify playlist import finished.")


if __name__ == "__main__":
    main()
