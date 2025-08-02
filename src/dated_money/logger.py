# dated_money.logger
# Copyright 2022 Juan Reyero
# SPDX-License-Identifier: MIT

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "dated_money",
    level: int = logging.INFO,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """Set up a logger for the dated_money package.

    Args:
        name: Logger name
        level: Logging level
        format_string: Custom format string for log messages

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Create formatter
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger


# Create a default logger for the package
logger = setup_logger()
