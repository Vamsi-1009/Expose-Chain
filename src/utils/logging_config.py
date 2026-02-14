"""
Logging configuration for ExposeChain
"""
import logging
import sys


def setup_logging():
    """Configure application logging"""
    logger = logging.getLogger("exposechain")
    logger.setLevel(logging.DEBUG)

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(handler)

    return logger
