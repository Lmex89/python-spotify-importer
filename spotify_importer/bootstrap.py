"""Startup/bootstrap utilities for environment and logging."""

import importlib
import os
from typing import Protocol
from urllib.parse import urlparse, urlunparse


class LoggerAbstract(Protocol):
    """Minimal logger interface used by this project."""

    def info(self, message: str) -> object: ...

    def warning(self, message: str) -> object: ...

    def success(self, message: str) -> object: ...

    def error(self, message: str) -> object: ...


def load_environment() -> None:
    """Load .env values via python-dotenv and fail with a clear dependency message."""
    try:
        dotenv_module = importlib.import_module("dotenv")
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency 'python-dotenv'. Install it with: pip install python-dotenv"
        ) from exc

    dotenv_module.load_dotenv()


def get_logger() -> LoggerAbstract:
    """Load loguru logger and fail with clear setup guidance if missing."""
    try:
        loguru_module = importlib.import_module("loguru")
    except ImportError as exc:
        raise SystemExit("Missing dependency 'loguru'. Install it with: pip install loguru") from exc

    return loguru_module.logger


def normalize_redirect_uri(logger: LoggerAbstract) -> None:
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
    logger.warning(f"SPOTIPY_REDIRECT_URI used localhost. Updated to loopback IP: {updated_uri}")
