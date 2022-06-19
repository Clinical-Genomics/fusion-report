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
        self.view: str = f"views/{view}.html"
        self.modules: Dict[str, Any] = {}
        self.filename: str = filename if filename else self._set_filename(title)

    def add_module(self, name: str, manager: FusionManager = None, params=None) -> None:
        """Add module to the list."""
        if name not in self.modules:
            self.modules[name] = ModuleLoader(manager, params).exec(name)
        else:
            Logger(__name__).warning("Module %s already loaded", name)

    def get_content(self) -> Dict[str, Any]:
        """Helper serialization method for templating engine."""
        return {"title": self.title, "filename": self.filename, "view": self.view}

    @staticmethod
    def _set_filename(fusion: str) -> str:
        """Helper function for setting proper filename.

        Args:
            fusion ([str]): Fusion name

        Returns:
            str: filename of the fusion
        """
        for char in ["/", "\\", "--"]:
            if char in fusion:
                fusion = fusion.replace(char, "_")

        return f"{fusion}.html"
