from typing import Any, Dict
from fusion_report.data.fusiongdb import FusionGDB
from fusion_report.modules.base_module import BaseModule


class CustomModule(BaseModule):

    def get_data(self) -> Dict[str, Any]:
        return FusionGDB(self.params['db_path']).select(
            '''
            SELECT gene_symbol, drug_status, drug_bank_id, drug_name, drug_action,
            fusion_uniprot_related_drugs.uniprot_acc FROM fusion_uniprot_related_drugs
            INNER JOIN uniprot_gsymbol
            ON fusion_uniprot_related_drugs.uniprot_acc = uniprot_gsymbol.uniprot_acc
            WHERE gene_symbol = ? OR gene_symbol = ?
            ''',
            self.params['fusion'].split('--')
        )

    def load(self) -> Dict[str, Any]:
        return {
            'data': self.get_data(),
            'menu': ['Targeting drugs']
        }
