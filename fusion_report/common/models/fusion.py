from typing import Any, Dict, List

class Fusion:

    def __init__(self, name):
        self.name: str = name
        self.score: Dict[str, Any] = {}
        self.dbs: List[str] = []
        self.tools: Dict = {}

    def add_tool(self, tool: str, details: Dict[str, Any]):
        if tool and tool not in self.tools.keys():
            self.tools[tool] = details
