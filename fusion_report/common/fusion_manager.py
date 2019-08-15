from typing import Any, Dict, List, Set
from fusion_report.common.models.fusion import Fusion
from fusion_report.common.logger import Logger


class FusionManager:

    def __init__(self, settings):
        self.__running_tools: Set[str] = set()
        self.__fusions: List[Fusion] = []
        self.__supported_tools: List[str] = [
            tool['key'].replace('--', '') for tool in settings['args']['run']['tools']
        ]

    def parse(self, tool, file) -> None:
        if tool in self.__supported_tools:
            self.__running_tools.add(tool)
            factory_parser = self.__build_factory(tool)
            with open(file, 'r', encoding='utf-8') as f:
                next(f)  # skip header line
                for line in f:
                    fusion_name, details = factory_parser.parse(line)
                    self.add(fusion_name, tool, details)
                    # enrich with DB
        else:
            Logger().get_logger().warning(
                'Tool %s is not supported. To integrate the tool please create an issue', tool
            )

    def add(self, name: str, tool: str, details: Dict[str, Any]) -> None:
        if name and tool:
            index = self.__index_off(name)
            if index == -1:
                fusion = Fusion(name)
                fusion.add_tool(tool, details)
                self.__fusions.append(fusion)
            else:
                fusion = self.__fusions[index]
                fusion.add_tool(tool, details)

    def get_supported_tools(self) -> List[str]:
        return self.__supported_tools

    def get_running_tools(self) -> Set[str]:
        return self.__running_tools

    def get_fusions(self) -> List[Fusion]:
        return self.__fusions

    def get_known_fusions(self) -> List[Fusion]:
        known: List[Fusion] = []
        [known.append(fusion) for fusion in self.__fusions if fusion.get_databases()]
        return known

    ################################################################################################
    #  Helpers
    @classmethod
    def __build_factory(cls, tool: str):
        module_name: str = f'fusion_report.parsers.{tool.lower()}'
        module = __import__(module_name, fromlist=[tool.capitalize()])
        klass = getattr(module, tool.capitalize())
        return klass()

    def __index_off(self, value: str) -> int:
        for index, fusion in enumerate(self.__fusions):
            if fusion.get_name() == value:
                return index
        return -1

    def print(self):
        for fusion in self.__fusions:
            print(f'{fusion.get_name()}: {len(fusion.get_tools())}')
            # print(f'{fusion.name}: {fusion.tools}')
