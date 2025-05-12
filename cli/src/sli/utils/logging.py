# Reference:
# https://alexandra-zaharia.github.io/posts/make-your-own-custom-color-formatter-with-python-logging/

import logging


class CustomFormatter(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    blue = "\x1b[38;5;33m"
    light_blue = "\x1b[38;5;45m"
    reset = "\x1b[0m"

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.light_blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset,
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


_LOGGER_NAME = "logger"
_FORMAT = "%(message)s"

logger = logging.getLogger(_LOGGER_NAME)
logger.setLevel(logging.DEBUG)

_formatter = CustomFormatter(_FORMAT)

_stream_handler = logging.StreamHandler()
_stream_handler.setFormatter(_formatter)

logger.addHandler(_stream_handler)
