from typing import Any, Dict
from fusion_report.modules.base_module import BaseModule


class CustomModule(BaseModule):

    def load(self) -> Dict[str, Any]:
        return {
            'fusion': self.params['fusion'],
            'menu': []
        }
