"""Base module for CustomModules"""
from typing import Any, Dict

from fusion_report.common.fusion_manager import FusionManager


class BaseModule:
    """Parent class for CustomModule."""

    def __init__(self, manager: FusionManager = None, params=None) -> None:
        self.manager: FusionManager = manager
        self.params: Dict[str, Any] = params
