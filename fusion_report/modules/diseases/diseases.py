from typing import Any, Dict, List
from fusion_report.data.fusiongdb import FusionGDB
from fusion_report.modules.base_module import BaseModule


class CustomModule(BaseModule):

    def get_data(self) -> Dict[str, Any]:
        return FusionGDB(self.params['db_path']).select(
            '''
            SELECT * FROM fgene_disease_associations
            WHERE (gene = ? OR gene = ?)
            AND disease_prob > 0.2001 ORDER BY disease_prob DESC
            ''',
            self.params['fusion'].split('--')
        )

    def load(self) -> Dict[str, Any]:
        return {
            'data': self.get_data(),
            'menu': ['Related diseases']
        }
