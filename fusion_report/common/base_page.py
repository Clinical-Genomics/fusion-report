import os
from typing import Any, Dict
from fusion_report.common.logger import Logger
from fusion_report.modules.loader import ModuleLoader
from fusion_report.common.fusion_manager import FusionManager


class BasePage:
    """Class defining main MasterPage. Variables are inherited for all created Pages (class Page)"""

    def __init__(self, title, filename, view):
        self.__title = title
        if filename:
            self.__filename = filename
        else:
            self.__filename = title.replace('--', '_') + ".html"
        self.__view = f'views/{view}.html'
        self.__modules: Dict[str, Any] = {}

    def add_module(self, name, manager: FusionManager = None, params=None) -> None:
        if name not in self.__modules:
            self.__modules[name] = ModuleLoader(manager, params).exec(name)
        else:
            Logger().get_logger().warning(f'Module {name} already loaded')

    def get_modules(self) -> Dict[str, Any]:
        return self.__modules

    def get_title(self) -> str:
        """ Method returning title of the page."""
        return self.__title

    def get_filename(self) -> str:
        """ Method returning name of the page."""
        return self.__filename

    def get_view(self) -> str:
        return self.__view

    def get_content(self) -> Dict[str, Any]:
        """Helper method returning all variables. Used for Jinja templating"""
        return {
            'title': self.get_title(),
            'filename': self.get_filename(),
            'view': self.get_view()
        }
