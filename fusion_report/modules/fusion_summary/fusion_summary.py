"""Fusion summary module"""
from typing import Any, Dict

from fusion_report.modules.base_module import BaseModule


class CustomModule(BaseModule):
    """Fusion summary section in fusion page"""

    def load(self) -> Dict[str, Any]:
        """Return module variables."""
        return {"fusion": self.params["fusion"], "menu": ["Summary"]}
