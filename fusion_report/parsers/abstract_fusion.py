import typing
import abc

class AbstractFusionTool(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def parse(self, line, delimiter=None):
        """ Parsing method required to be implemented per fusion tool."""
