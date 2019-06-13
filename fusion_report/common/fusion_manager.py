from typing import Any, Dict, List
from fusion_report.common.models.fusion import Fusion
from fusion_report.logger import Logger

class FusionManager:

    def __init__(self, tools):
        self.supported_tools = tools
        self.log = Logger().get_logger()
        self.fusions: List[Fusion] = []
        # self.db = Db()

    def parse(self, tool, file):
        if tool in self.supported_tools:
            factory_parser = self.__build_factory(tool)
            with open(file, 'r', encoding='utf-8') as f:
                next(f) # skip header line
                for line in f:
                    fusion_name, details = factory_parser.parse(line)
                    self.add(fusion_name, tool, details)
                    # enrich with DB
        else:
            self.log.warning(
                f'Tool {tool} is not supported. To integrate the tool please create an issue'
            )

    def __index_off(self, key, value):
        for index, fusion in enumerate(self.fusions):
            if getattr(fusion, key) == value:
                return index
        return -1

    def add(self, name: str, tool: str, details: Dict[str, Any]) -> None:
        if name and tool:
            index = self.__index_off('name', name)
            if index == -1:
                fusion = Fusion(name)
                fusion.add_tool(tool, details)
                self.fusions.append(fusion)
            else:
                fusion = self.fusions[index]
                fusion.add_tool(tool, details)

    def __build_factory(self, tool):
        module_name: str = f'fusion_report.parsers.{tool.lower()}'
        module = __import__(module_name, fromlist=[tool.capitalize()])
        klass = getattr(module, tool.capitalize())
        return klass()

    def print(self):
        for fusion in self.fusions:
            print(f'{fusion.name}: {len(fusion.tools)}')
            # print(f'{fusion.name}: {fusion.tools}')
