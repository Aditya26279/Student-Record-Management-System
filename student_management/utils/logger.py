"""
utils/logger.py — Centralised logging configuration
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

LOG_DIR  = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "srms.log")

# Coloured console formatter (ANSI)
COLOURS = {
    "DEBUG":    "\033[36m",   # cyan
    "INFO":     "\033[32m",   # green
    "WARNING":  "\033[33m",   # yellow
    "ERROR":    "\033[31m",   # red
    "CRITICAL": "\033[1;31m", # bold red
    "RESET":    "\033[0m",
}


class ColouredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        colour = COLOURS.get(record.levelname, "")
        reset  = COLOURS["RESET"]
        record.levelname = f"{colour}{record.levelname:8s}{reset}"
        return super().format(record)


def setup_logger(name: str = "srms",
                 level: int = logging.INFO,
                 enable_file: bool = True) -> logging.Logger:
    """Return a named logger with console + optional rotating file handler."""
    logger = logging.getLogger(name)
    if logger.handlers:          # prevent duplicate handlers on re-import
        return logger

    logger.setLevel(level)

    # ── Console handler ──────────────────────────────────────────────────
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(ColouredFormatter(
        fmt="%(levelname)s %(name)s — %(message)s"
    ))
    logger.addHandler(ch)

    # ── Rotating file handler ────────────────────────────────────────────
    if enable_file:
        os.makedirs(LOG_DIR, exist_ok=True)
        fh = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3,
                                 encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(
            fmt="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        logger.addHandler(fh)

    return logger


# Module-level default logger
log = setup_logger()
