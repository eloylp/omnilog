# coding=utf-8

import logging
from omnilog.strings import Strings


class Logger(object):
    """
    Wrapper class for logging
    """

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(Strings.APP_NAME)
        self.logger.setLevel(logging.INFO)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

    def emergency(self, message):
        self.logger.emergency(message)
