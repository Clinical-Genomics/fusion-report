from typing import Any, Dict

from fusion_report.data.fusiongdb import FusionGDB
from fusion_report.modules.base_module import BaseModule


class CustomModule(BaseModule):

    def get_data(self) -> Dict[str, Any]:
        return FusionGDB(self.params['db_path']).select(
            '''
            SELECT * FROM tcga_chitars_combined_fusion_information_on_hg19
            WHERE h_gene = ? AND t_gene = ?
            ''',
            self.params['fusion'].split('--')
        )

    def load(self) -> Dict[str, Any]:
        return {
            'data': self.get_data(),
            'menu': ['Fusion gene variations']
        }
