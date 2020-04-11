"""Ensembl transcript module"""
from typing import Any, Dict

from fusion_report.data.fusiongdb import FusionGDB
from fusion_report.modules.base_module import BaseModule


class CustomModule(BaseModule):
    """Differently observed Ensembl transcripts in fusion page."""

    def get_data(self) -> Dict[str, Any]:
        """Gathers necessary data."""

        return FusionGDB(self.params['db_path']).select(
            '''
            SELECT * FROM tcga_chitars_combined_fusion_ORF_analyzed_gencode_h19v19
            WHERE h_gene = ? AND t_gene = ?
            ''',
            self.params['fusion'].split('--')
        )

    def load(self) -> Dict[str, Any]:
        """Return module variables."""

        return {
            'data': self.get_data(),
            'menu': ['Ensembl transcripts']
        }
