# -*- coding: utf-8 -*-
"""Various functions for logging."""
import os
import logging
from logging.handlers import RotatingFileHandler


def set_logger():
    """Sets logger."""
    logs_dir = os.getenv("METRICS_LOGS_PATH")
    if logs_dir:
        log_path = os.path.join(logs_dir, 'ace_client.log')
    else:
        log_path = os.path.join('log', 'ace_client.log')
    # It means DEBUG level - https://docs.python.org/2.7/library/logging.html#levels
    log_level = 10
    logger = logging.getLogger("ace_client_logger")
    max_file_size = 1024 * 1024 * 10
    if not len(logger.handlers):
        logger.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(filename)s --> %(funcName)s - %(levelname)s - %(message)s')
        handler = RotatingFileHandler(log_path, maxBytes=max_file_size, backupCount=3, encoding='utf-8')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
