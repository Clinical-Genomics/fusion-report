from typing import Any, Dict, List
from fusion_report.modules.base_module import BaseModule


class CustomModule(BaseModule):

    def load(self) -> Dict[str, Any]:
        return {
            'fusion': self.params['fusion'],
            'menu': []
        }
