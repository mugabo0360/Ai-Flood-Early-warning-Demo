"""Project-wide logging setup."""

from __future__ import annotations

import logging
import os

_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
_configured = False


def get_logger(name: str, level: str | None = None) -> logging.Logger:
    """Return a logger, configuring the root handler once.

    Args:
        name: Logger name, usually ``__name__``.
        level: Log level; defaults to the ``LOG_LEVEL`` env var or ``INFO``.
    """
    global _configured
    if not _configured:
        logging.basicConfig(format=_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
        _configured = True
    logger = logging.getLogger(name)
    logger.setLevel((level or os.getenv("LOG_LEVEL", "INFO")).upper())
    return logger
