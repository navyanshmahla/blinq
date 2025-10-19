import logging
import sys
import os
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler

def setup_app_logger():
    logger = logging.getLogger("app")
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level))
    logger.propagate = False

    if logger.hasHandlers():
        return logger

    log_format = "%(timestamp)s %(level)s %(logger)s %(message)s"

    formatter = jsonlogger.JsonFormatter(
        log_format,
        rename_fields={
            "levelname": "level",
            "name": "logger",
            "asctime": "timestamp"
        },
        timestamp=True
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if os.getenv("LOG_TO_FILE", "true").lower() == "true":
        log_file = os.getenv("APP_LOG_FILE", "logs/app.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logging.LoggerAdapter(logger, {"service": "app"})

app_logger = setup_app_logger()
