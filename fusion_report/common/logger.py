""" Application logger """
import logging
import sys
from logging.handlers import TimedRotatingFileHandler

from colorlog import ColoredFormatter

from fusion_report.common.singleton import Singleton


class Logger(metaclass=Singleton):
    """Wrapper around logging.

    Attributes:
        __logger: Logger instance
    """
    __logger = None

    def __init__(self) -> None:
        self.__logger = logging.getLogger('fusion-report')

        console_handler = logging.StreamHandler(sys.stdout)
        formatter = \
            '%(asctime)s %(log_color)s%(levelname)s%(reset)s | %(log_color)s%(message)s%(reset)s'
        console_handler.setFormatter(ColoredFormatter(formatter))
        self.__logger.addHandler(console_handler)

        self.file = 'fusion_report.log'
        file_handler = TimedRotatingFileHandler(self.file, when='midnight')
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.ERROR)
        self.__logger.addHandler(file_handler)

        self.__logger.setLevel(logging.DEBUG)
        self.__logger.propagate = False

    def get_logger(self) -> logging.Logger:
        """Returns logger instance"""
        return self.__logger
