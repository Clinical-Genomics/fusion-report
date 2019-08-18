""" Fusion Model """
from typing import Any, Dict, List

from fusion_report.common.logger import Logger


class Fusion:
    """Represents all required properties defining a fusion between two genes.

    Attributes:
        __name: Fusion name
        __score: Fusion score, attributes: `score` and `explained`
        __dbs: List of databases where fusion was found
        __tools: List of tools which detected fusion
    """
    def __init__(self, name: str) -> None:
        self.__name: str = name
        self.__score: Dict[str, Any] = {}
        self.__dbs: List[str] = []
        self.__tools: Dict[str, Any] = {}

    def get_name(self) -> str:
        """Returns fusion name."""
        return self.__name

    def get_tools(self) -> Dict[str, Any]:
        """
        Returns list of tools which were able to detect a fusion.

        Returns:
            tools: list of tools
        """
        return self.__tools

    def get_databases(self) -> List[str]:
        """Returns list of databases where fusion was found."""
        return self.__dbs

    def set_score(self, score: float, explained: str) -> None:
        """Sets calculated score."""
        self.__score = {
            'score': score,
            'explained': explained
        }

    def get_score(self) -> float:
        """Returns estimated score."""
        return self.__score['score']

    def get_score_explained(self) -> str:
        """Returns explanation of how the score was calculated."""
        return self.__score['explained']

    def add_tool(self, tool: str, details: Dict[str, Any]) -> None:
        """Add new fusion tool to the list."""
        if tool and tool not in self.__tools.keys():
            self.__tools[tool] = details
        else:
            Logger(__name__).debug('Tool %s already in list or empty', tool)

    def add_db(self, database: str) -> None:
        """Add new database to the list."""
        if database and database not in self.__dbs:
            self.__dbs.append(database)
        else:
            Logger(__name__).debug('Database %s already in list or empty', database)

    def json_serialize(self) -> Dict[str, Any]:
        """Helper serialization method for templating engine."""
        json = {
            'Fusion': self.get_name(),
            'Databases': self.get_databases(),
            'Score': self.get_score(),
            'Explained score': self.get_score_explained(),
        }
        json.update(self.get_tools())
        return json
