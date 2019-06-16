from fusion_report.common.logger import Logger
from typing import Any, Dict, List

class Fusion:

    def __init__(self, name):
        self.name: str = name
        self.score: Dict[str, Any] = {}
        self.dbs: List[str] = []
        self.tools: Dict[str, Any] = {}

    def get_name(self) -> str:
        return self.name

    def get_tools(self) -> Dict[str, Any]:
        return self.tools.items()

    def get_databases(self) -> List[str]:
        return self.dbs

    def set_score(self, score: float, explained: str) -> None:
        self.score = {
            'score': score,
            'explained': explained
        }

    def add_tool(self, tool: str, details: Dict[str, Any]) -> None:
        if tool and tool not in self.tools.keys():
            self.tools[tool] = details
        else:
            Logger().get_logger().warning('Tool %s already in list or empty', tool)

    def add_db(self, database: str) -> None:
        if database and database not in self.dbs:
            self.dbs.append(database)
        else:
            Logger().get_logger().warning('Database %s already in list or empty', database)
