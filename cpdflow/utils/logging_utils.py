import logging
import logging.config

LOGGING_LINE_FORMAT = "%(asctime)s %(levelname)s %(name)-30s : %(message)s"
LOGGING_LINE_ERROR_FORMAT = "%(asctime)s-%(levelname)s-%(name)s-%(process)d::%(module)s|%(lineno)s:: %(message)s"
LOGGING_DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S"


def _configure_loggers(root_module_name):
    configDict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"standard": {"format": LOGGING_LINE_FORMAT, "datefmt": LOGGING_DATETIME_FORMAT}, "error": {"format": LOGGING_LINE_FORMAT, "datefmt": LOGGING_DATETIME_FORMAT}},
        "handlers": {
            "console": {"class": "logging.StreamHandler", "level": "DEBUG", "formatter": "standard"},
            "info_rotating_file_handler": {"level": "INFO", "formatter": "standard", "class": "logging.FileHandler", "filename": "./logs/cpdflow-info.log", "mode": "w", "encoding": "utf-8",},
            "error_file_handler": {"level": "WARNING", "formatter": "error", "class": "logging.FileHandler", "filename": "./logs/cpdflow-error.log", "mode": "w",},
        },
        "loggers": {root_module_name: {"handlers": ["console", "info_rotating_file_handler", "error_file_handler"], "level": "INFO", "propagate": False}},
    }
    logging.config.dictConfig(configDict)

