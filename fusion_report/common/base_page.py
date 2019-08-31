""" Parent class of Page """
from typing import Any, Dict

from fusion_report.common.fusion_manager import FusionManager
from fusion_report.common.logger import Logger
from fusion_report.modules.loader import ModuleLoader


class BasePage:
    """The class implements core methods.

    Attributes:
        title: Title of the page
        filename: Optional, either fusion name (AKAP9_BRAF.html) or anything else (index.html)
        view: View
        modules: Custom modules
    """
    def __init__(self, title: str, view: str, filename: str = None) -> None:
        self.title: str = title.strip()
        self.view: str = f'views/{view}.html'
        self.modules: Dict[str, Any] = {}
        if filename:
            self.filename: str = filename
        else:
            self.filename: str = title.replace('--', '_') + ".html"

    def add_module(self, name: str, manager: FusionManager = None, params=None) -> None:
        """Add module to the list."""
        if name not in self.modules:
            self.modules[name] = ModuleLoader(manager, params).exec(name)
        else:
            Logger(__name__).warning('Module %s already loaded', name)

    def get_content(self) -> Dict[str, Any]:
        """Helper serialization method for templating engine."""
        return {
            'title': self.title,
            'filename': self.filename,
            'view': self.view
        }
