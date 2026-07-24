"""Application logging for Scribe."""

from __future__ import annotations

import logging
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path.home() / "Library" / "Logs" / "Scribe"
LOG_FILE = LOG_DIR / "app.log"

_configured = False


def setup_logging() -> logging.Logger:
    """Configure rotating file logging and return the app logger."""
    global _configured
    logger = logging.getLogger("local_transcriber")
    if _configured:
        return logger

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    _configured = True
    return logger


def get_logger() -> logging.Logger:
    if not _configured:
        return setup_logging()
    return logging.getLogger("local_transcriber")


def log_exception(message: str) -> None:
    logger = get_logger()
    logger.error("%s\n%s", message, traceback.format_exc())
