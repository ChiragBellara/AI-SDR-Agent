import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def setup_logger(name: str = "ai_sdr") -> logging.Logger:
    """
    Sets up a logger with:
    - Console handler (readable)
    - Rotating file handler logs/app.log (keeps history)
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(DEFAULT_LOG_LEVEL)
    logger.propagate = False

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console
    console = logging.StreamHandler()
    console.setLevel(DEFAULT_LOG_LEVEL)
    console.setFormatter(fmt)
    logger.addHandler(console)

    # File (rotating)
    file_path = LOG_DIR / "app.log"
    file_handler = RotatingFileHandler(
        file_path,
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(DEFAULT_LOG_LEVEL)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger
