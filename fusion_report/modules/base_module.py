from typing import Any, Dict
from fusion_report.common.fusion_manager import FusionManager


class BaseModule:

    def __init__(self, manager: FusionManager = None, params=None):
        self.manager: FusionManager = manager
        self.params: Dict[str, Any] = params
