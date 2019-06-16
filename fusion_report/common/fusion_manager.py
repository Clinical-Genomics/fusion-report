from typing import Any, Dict, List
from fusion_report.common.models.fusion import Fusion
from fusion_report.common.logger import Logger

class FusionManager:

    def __init__(self, settings):
        self.log = Logger().get_logger()
        self.__fusions: List[Fusion] = []
        self.__supported_tools: List[str] = [
            tool['key'].replace('--', '') for tool in settings['args']['run']['tools']
        ]

    def parse(self, tool, file):
        if tool in self.__supported_tools:
            factory_parser = self.__build_factory(tool)
            with open(file, 'r', encoding='utf-8') as f:
                next(f) # skip header line
                for line in f:
                    fusion_name, details = factory_parser.parse(line)
                    self.add(fusion_name, tool, details)
                    # enrich with DB
        else:
            self.log.warning(
                'Tool %s is not supported. To integrate the tool please create an issue', tool
            )

    def add(self, name: str, tool: str, details: Dict[str, Any]) -> None:
        if name and tool:
            index = self.__index_off('name', name)
            if index == -1:
                fusion = Fusion(name)
                fusion.add_tool(tool, details)
                self.__fusions.append(fusion)
            else:
                fusion = self.__fusions[index]
                fusion.add_tool(tool, details)

    def get_supported_tools(self):
        return self.__supported_tools

    def get_fusions(self) -> List[Fusion]:
        return self.__fusions

    ################################################################################################
    #  Helpers
    def __build_factory(self, tool):
        module_name: str = f'fusion_report.parsers.{tool.lower()}'
        module = __import__(module_name, fromlist=[tool.capitalize()])
        klass = getattr(module, tool.capitalize())
        return klass()

    def __index_off(self, key, value):
        for index, fusion in enumerate(self.__fusions):
            if getattr(fusion, key) == value:
                return index
        return -1

    def print(self):
        for fusion in self.__fusions:
            print(f'{fusion.name}: {len(fusion.tools)}')
            # print(f'{fusion.name}: {fusion.tools}')
