import abc

class AbstractFusionTool(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def parse(self, line):
        """ Parsing method required to be implemented per fusion tool."""
