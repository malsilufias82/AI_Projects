"""
logger.py
---------
Centralized logging configuration for the Status Report Bot.

Provides a single get_logger() factory so every module logs to the
same rotating file (and console) with a consistent format.
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def get_logger(name: str, logs_folder: str = "./logs", level: str = "INFO") -> logging.Logger:
    """
    Create (or fetch) a configured logger.

    Args:
        name: Logger name, typically __name__ of the calling module.
        logs_folder: Directory where log files should be written.
        level: Logging level as a string (e.g. "INFO", "DEBUG").

    Returns:
        A configured logging.Logger instance.
    """
    os.makedirs(logs_folder, exist_ok=True)

    logger = logging.getLogger(name)

    # Avoid attaching duplicate handlers if this is called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotating file handler: 5 MB per file, keep 5 backups
    file_handler = RotatingFileHandler(
        os.path.join(logs_folder, "status_report_bot.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
