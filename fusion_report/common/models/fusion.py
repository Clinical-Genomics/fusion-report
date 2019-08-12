from fusion_report.common.logger import Logger
from typing import Any, Dict, List


class Fusion:

    def __init__(self, name):
        self.__name: str = name
        self.__score: Dict[str, Any] = {}
        self.__dbs: List[str] = []
        self.__tools: Dict[str, Any] = {}

    def get_name(self) -> str:
        return self.__name

    def get_tools(self) -> Dict[str, Any]:
        return self.__tools

    def get_databases(self) -> List[str]:
        return self.__dbs

    def set_score(self, score: float, explained: str) -> None:
        self.__score = {
            'score': score,
            'explained': explained
        }

    def get_score(self) -> float:
        return self.__score['score']

    def get_score_explained(self) -> str:
        return self.__score['explained']

    def add_tool(self, tool: str, details: Dict[str, Any]) -> None:
        if tool and tool not in self.__tools.keys():
            self.__tools[tool] = details
        else:
            Logger().get_logger().warning('Tool %s already in list or empty', tool)

    def add_db(self, database: str) -> None:
        if database and database not in self.__dbs:
            self.__dbs.append(database)
        else:
            Logger().get_logger().warning('Database %s already in list or empty', database)

    def json_serialize(self):
        json = {
            'Fusion': self.get_name(),
            'Databases': self.get_databases(),
            'Score': self.get_score(),
            'Explained score': self.get_score_explained(),
        }
        json.update(self.get_tools())
        return json
