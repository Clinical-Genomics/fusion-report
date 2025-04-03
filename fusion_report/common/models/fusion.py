""" Fusion Model """
from typing import Any, Dict, List

from fusion_report.common.logger import Logger


class Fusion:
    """Represents all required properties defining a fusion between two genes.

    Attributes:
        name: Fusion name
        score: Fusion Indication Index, attributes: `score` and `explained`
        dbs: List of databases where fusion was found
        tools: List of tools which detected fusion
    """

    def __init__(self, name: str) -> None:
        self.name: str = name.strip()
        self._score: Dict[str, Any] = {"score": 0, "explained": ""}
        self.dbs: List[str] = []
        self.tools: Dict[str, Any] = {}

    @property
    def score(self) -> float:
        return self._score["score"]

    @score.setter
    def score(self, value: float) -> None:
        self._score["score"] = float(value)

    @property
    def score_explained(self) -> str:
        """Returns explanation of how the FII was calculated."""
        return self._score["explained"]

    @score_explained.setter
    def score_explained(self, value: str) -> None:
        self._score["explained"] = value

    def add_tool(self, tool: str, details: Dict[str, Any]) -> None:
        """Add new fusion tool to the list."""
        if tool and tool not in self.tools.keys():
            self.tools[tool] = details
        else:
            Logger(__name__).debug("Tool %s already in list or empty", tool)

    def add_db(self, database: str) -> None:
        """Add new database to the list."""
        if database and database not in self.dbs:
            self.dbs.append(database)
        else:
            Logger(__name__).debug("Database %s already in list or empty", database)

    def json_serialize(self) -> Dict[str, Any]:
        """Helper serialization method for templating engine."""
        json: Dict[str, Any] = {
            "Fusion": self.name,
            "Databases": self.dbs,
            "Fusion Indication Index (FII)": self.score,
            "Explained FII": self.score_explained,
        }

        return {**json, **self.tools}
