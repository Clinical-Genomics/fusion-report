""" Fusion Manager """
from typing import Any, Dict, List, Set, Tuple

from fusion_report.common.exceptions.app import AppException
from fusion_report.common.logger import Logger
from fusion_report.common.models.fusion import Fusion


class FusionManager:
    """Core manager handling fusion detection tool output parsing. It contains collection of
       individual parsed fusion.

    Attributes:
        fusions: List of parsed fusions
        running_tools: List of executed fusion detection tools
        supported_tools: List of all supported fusion detection tools
    """

    def __init__(self, supported_tools: List[str]) -> None:
        self.fusions: List[Fusion] = []
        self.running_tools: Set[str] = set()
        self.supported_tools: List[str] = supported_tools

    def parse(self, tool: str, file: str, allow_multiple_genes: bool) -> None:
        """Loads a parser for specific tool by its name and stored the results.

        Raises:
            AppException
        """
        if tool in self.supported_tools:
            self.running_tools.add(tool)
            factory_parser = self.__build_factory(tool)
            try:
                with open(file, "r", encoding="utf-8") as fusion_output:
                    factory_parser.set_header(
                        fusion_output.readline().replace('"', "").strip()
                    )
                    for line in fusion_output:
                        line = line.replace('"', "").strip()
                        fusion_list: List[
                            Tuple[str, Dict[str, Any]]
                        ] = factory_parser.parse(line)
                        if allow_multiple_genes is None and len(fusion_list) > 1:
                            fusion_list = [fusion_list[0]]
                        for fusion_name, details in fusion_list:
                            self.add(fusion_name, tool, details)
            except IOError as ex:
                raise AppException(ex)
        else:
            Logger(__name__).error(
                "Tool %s is not supported. To integrate the tool please create an issue",
                tool,
            )

    def add(self, fusion_name: str, tool: str, details: Dict[str, Any]) -> None:
        """Insert of append new parsed information to specific fusion."""
        if fusion_name and tool:
            index = self.index_by(fusion_name)
            if index == -1:
                fusion = Fusion(fusion_name)
                fusion.add_tool(tool, details)
                self.fusions.append(fusion)
            else:
                fusion = self.fusions[index]
                fusion.add_tool(tool, details)

    def get_known_fusions(self) -> List[Fusion]:
        """Returns list of all fusions found in local databases."""
        return [fusion for fusion in self.fusions if fusion.dbs]

    ################################################################################################
    #  Helpers
    @staticmethod
    def __build_factory(tool: str):
        """Factory builder loads custom fusion detection tool parser based on its name. It then
        returns an instance of desired parser.

        Return:
            Instance of a tool parser

        Raises:
            AppException
        """
        try:
            module_name: str = f"fusion_report.parsers.{tool.lower()}"
            module = __import__(module_name, fromlist=[tool.capitalize()])
            klass = getattr(module, tool.capitalize())
            return klass()
        except AttributeError as ex:
            raise AppException(ex)

    def index_by(self, value: str) -> int:
        """Helper for finding fusion based on its name.

        Returns:
            >=0 index of a fusion in the list
            -1: not found
        """
        for index, fusion in enumerate(self.fusions):
            if fusion.name == value:
                return index
        return -1
