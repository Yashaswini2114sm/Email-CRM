import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    """
    Creates and configures a standard logger.
    Why? So all parts of our application log in the exact same format.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # We output logs to the console (sys.stdout)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # Standardizing what a log line looks like
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger if it doesn't already have one
    if not logger.handlers:
        logger.addHandler(handler)

    return logger
