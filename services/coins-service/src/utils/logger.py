import logging
import sys

from loguru import logger


def prepare_loggers(debug: bool):
    log_level = logging.getLevelName("DEBUG" if debug else "INFO")
    logging.root.setLevel(log_level)
    logger.remove()
    if debug:
        logger.add(sys.stderr, level=log_level, backtrace=True, diagnose=True)
    else:
        logger.add(sys.stderr, level=log_level, colorize=False, serialize=True)
    return log_level
