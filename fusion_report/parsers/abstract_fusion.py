"""Abstract Fusion module"""
import abc
from typing import Any, Dict, Tuple


class AbstractFusionTool(metaclass=abc.ABCMeta):
    """Abstract class requiring to implement parse method for every fusion detection tool parser."""

    @abc.abstractmethod
    def parse(self, line: str, delimiter: str = None) -> Tuple[str, Dict[str, Any]]:
        """ Parsing method required to be implemented per fusion tool."""
