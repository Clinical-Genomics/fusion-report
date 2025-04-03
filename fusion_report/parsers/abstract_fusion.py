"""Abstract Fusion module"""
import abc

from typing import Any, Dict, List, Tuple


class AbstractFusionTool(metaclass=abc.ABCMeta):
    """Abstract class requiring to implement parse method for every fusion detection tool parser."""

    @abc.abstractmethod
    def set_header(self, header: str, delimiter: str | None = None):
        """Set header."""

    @abc.abstractmethod
    def parse(self, line: str, delimiter: str | None = None) -> List[Tuple[str, Dict[str, Any]]]:
        """Parsing method required to be implemented per fusion tool."""
