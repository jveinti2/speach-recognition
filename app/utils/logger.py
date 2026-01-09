import logging
import sys
from app.config import settings


def setup_logger(name: str = "speach-recognition-api") -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    formatter = logging.Formatter(
        '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "msg": "%(message)s"}'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


logger = setup_logger()
