import abc


class AbstractFusionTool(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def parse(self, line: str, delimiter: str = None):
        """ Parsing method required to be implemented per fusion tool."""
