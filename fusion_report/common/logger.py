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
        __filename: Logger file name
    """
    __logger = None

    def __init__(self, name: str) -> None:
        self.__logger = logging.getLogger(name)
        self.__filename = 'fusion_report.log'
        self.__logger.setLevel(logging.INFO)

    @staticmethod
    def get_logger() -> logging:
        """Return logger."""
        return logging.getLogger()

    def critical(self, msg: str, *args) -> None:
        """Critical logger."""
        self.__logger.addHandler(self.get_critical_handler(self.__filename))
        self.__logger.critical(msg, *args)

    def debug(self, msg: str, *args) -> None:
        """Debug logger."""
        self.__logger.addHandler(self.get_debug_handler())
        self.__logger.debug(msg, *args)

    def error(self, msg: str, *args) -> None:
        """Error logger."""
        self.__logger.addHandler(self.get_critical_handler(self.__filename))
        self.__logger.error(msg, *args)

    def fatal(self, msg, *args, **kwargs):
        """Fatal logger."""
        self.__logger.addHandler(self.get_critical_handler(self.__filename))
        self.__logger.fatal(msg, *args, **kwargs)

    def info(self, msg: str, *args) -> None:
        """Info logger."""
        self.__logger.addHandler(self.get_info_handler())
        self.__logger.info(msg, *args)

    def warning(self, msg: str, *args) -> None:
        """Warning logger."""
        self.__logger.addHandler(self.get_critical_handler(self.__filename))
        self.__logger.warning(msg, *args)

    @staticmethod
    def get_critical_handler(filename: str) -> TimedRotatingFileHandler:
        """Logging handler for levels: CRITICAL, ERROR and WARNING."""
        file_handler = TimedRotatingFileHandler(filename, when='midnight')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        )

        return file_handler

    @staticmethod
    def get_info_handler() -> logging.StreamHandler:
        """Logging handler for level INFO."""
        info_handler = logging.StreamHandler(sys.stdout)
        info_handler.setFormatter(ColoredFormatter('%(log_color)s%(message)s%(reset)s'))
        info_handler.setLevel(logging.INFO)

        return info_handler

    @staticmethod
    def get_debug_handler() -> logging.StreamHandler:
        """Logging handler for level DEBUG."""
        debug_handler = logging.StreamHandler(sys.stdout)
        debug_handler.setFormatter(ColoredFormatter(
            '%(log_color)s[%(levelname)s]%(reset)s %(log_color)s%(name)s%(reset)s - '
            '%(log_color)s%(message)s%(reset)s')
        )
        debug_handler.setLevel(logging.DEBUG)

        return debug_handler
