import logging

logging.basicConfig(level=logging.INFO)


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    This is a logger with the specified name and level.

    args:
        name (String): The name of the logger like root, database, discord, etc.
        level (Integer): The logging level by default it is logging.INFO.

    returns:
        logging.Logger: Configured logger instance.
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create console handler and set level
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # Create formatter and add it to the handler
    formatter = logging.Formatter(
        "%(asctime)s | %(name)-15s | %(levelname)-8s | %(message)s"
    )
    ch.setFormatter(formatter)

    # Add the handler to the logger
    if not logger.handlers:
        logger.addHandler(ch)

    return logger
