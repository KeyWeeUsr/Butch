"""Module containing all logging details."""

import logging
from os import environ


def get_logger():
    """
    Create a basic logger and return it.

    Returns:
        logging.RootLogger
    """
    logger = logging.getLogger(__name__)
    level = logging.INFO
    if environ.get("DEBUG"):
        level = logging.DEBUG
    logging.basicConfig(level=level, force=True)
    return logger
