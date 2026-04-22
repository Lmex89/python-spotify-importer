"""Input file reading and song title normalization."""

import re
from venv import logger


def clean_song_title(raw_title: str) -> str:
    """
    Sanitizes the input string for better search accuracy.
    Removes text in parentheses/brackets like '(Official Video)'.
    """
    logger.debug(f"Cleaning song title: '{raw_title}'")
    cleaned = re.sub(r"\(.*?\)|\[.*?\]", "", raw_title)
    cleaned = re.sub(
        r"Official Video|Official Music Video|4K|ft\\.",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned.strip()


def read_song_lines(input_file: str) -> list[str]:
    """Read non-empty lines from the input file."""
    with open(input_file, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]
