""" Parent class of Page """
from typing import Any, Dict

from fusion_report.common.fusion_manager import FusionManager
from fusion_report.common.logger import Logger
from fusion_report.modules.loader import ModuleLoader


class BasePage:
    """The class implements core methods.

    Attributes:
        __title: Title of the page
        __filename: Optional, either fusion name (AKAP9_BRAF.html) or anything else (index.html)
        __view: View
        __modules: Custom modules
    """
    def __init__(self, title: str, view: str, filename: str = None) -> None:
        self.__title: str = title
        self.__view: str = f'views/{view}.html'
        self.__modules: Dict[str, Any] = {}
        if filename:
            self.__filename: str = filename
        else:
            self.__filename: str = title.replace('--', '_') + ".html"

    def add_module(self, name: str, manager: FusionManager = None, params=None) -> None:
        """Add module to the list."""
        if name not in self.__modules:
            self.__modules[name] = ModuleLoader(manager, params).exec(name)
        else:
            Logger(__name__).warning('Module %s already loaded', name)

    def get_modules(self) -> Dict[str, Any]:
        """Return modules and their properties."""
        return self.__modules

    def get_title(self) -> str:
        """Returns page title."""
        return self.__title

    def get_filename(self) -> str:
        """Returns name of the HTML file."""
        return self.__filename

    def get_view(self) -> str:
        """Returns view template."""
        return self.__view

    def get_content(self) -> Dict[str, Any]:
        """Helper serialization method for templating engine."""
        return {
            'title': self.get_title(),
            'filename': self.get_filename(),
            'view': self.get_view()
        }
