import os
from typing import Any, Dict
from fusion_report.common.logger import Logger
from fusion_report.modules.loader import ModuleLoader


class BasePage:
    """Class defining main MasterPage. Variables are inherited for all created Pages (class Page)"""

    def __init__(self, title, view):
        self.__title = title
        self.__filename = title.replace('--', '_') + ".html"
        self.__view = f'views/{view}.html'
        self.__modules: Dict[str, Any] = {}

    def add_module(self, name, manager=None):
        if name not in self.__modules:
            self.__modules[name] = ModuleLoader(manager).exec(name)
        else:
            Logger().get_logger().warning(f'Module {name} already loaded')

    def get_modules(self) -> Dict[str, Any]:
        return self.__modules

    def get_title(self):
        """ Method returning title of the page."""
        return self.__title

    def get_filename(self):
        """ Method returning name of the page."""
        return self.__filename

    def get_content(self):
        """Helper method returning all variables. Used for Jinja templating"""
        return {
            'title': self.__title,
            'filename': self.__filename,
            'dynamic_partial': self.__view
        }
