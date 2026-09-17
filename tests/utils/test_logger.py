import logging

from app.utils.logger import setup_logger


def test_setup_logger_returns_configured_logger():
    logger = setup_logger("test-logger", level=logging.DEBUG)
    assert logger.name == "test-logger"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 1


def test_setup_logger_does_not_duplicate_handlers_on_repeated_calls():
    first = setup_logger("dedup-logger")
    second = setup_logger("dedup-logger")
    assert first is second
    assert len(second.handlers) == 1
