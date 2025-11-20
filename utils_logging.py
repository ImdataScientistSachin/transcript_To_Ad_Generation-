"""Lightweight logging helpers used throughout the project.

This module centralizes a tiny logging configuration so other modules
can call `configure_logging()` once at startup and use `get_logger()` to
create named loggers. This keeps console output consistent for local
development and CI runs.

The helpers intentionally avoid complex handlers — the project is a
small prototype and the default console logger is sufficient for
debugging and development.
"""
import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure the root logger for the application.

    Args:
        level: Logging level name (e.g., "DEBUG", "INFO").
    """
    fmt = "%(asctime)s %(levelname)s %(name)s - %(message)s"
    logging.basicConfig(level=getattr(logging, level), format=fmt)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger for the caller module.

    Use this rather than `logging.getLogger` directly to keep call sites
    consistent and to make it easier to change logging behavior globally
    in one place later.
    """
    return logging.getLogger(name)
