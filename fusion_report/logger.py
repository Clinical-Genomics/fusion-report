import logging
import sys
from logging.handlers import TimedRotatingFileHandler

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Logger(metaclass=Singleton):

    __logger = None

    def __init__(self):
        self.formatter = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
        self.file = 'fusion_report.log'
        self.__logger = logging.getLogger('fusion-report')

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter)
        self.__logger.addHandler(console_handler)

        file_handler = TimedRotatingFileHandler(self.file, when='midnight')
        file_handler.setFormatter(self.formatter)
        self.__logger.addHandler(file_handler)

        self.__logger.setLevel(logging.DEBUG)
        self.__logger.propagate = False

    def get_logger(self):
        return self.__logger
