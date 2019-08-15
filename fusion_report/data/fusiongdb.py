from typing import List
from fusion_report.common.db import Db
from fusion_report.common.singleton import Singleton


class FusionGDB(Db, metaclass=Singleton):

    def __init__(self, path):
        super().__init__(path, 'FusionGDB', 'FusionGDB.sql')

    def setup(self, files: List[str], delimiter: str = '', skip_header=False, encoding='utf-8'):
        super().setup(files, delimiter)
        # additional customization
        sql = '''UPDATE tcga_chitars_combined_fusion_orf_analyzed_gencode_h19v19
                 SET orf = "Frame-shift" WHERE orf = "Frame-shit"
        '''
        self.execute(sql)

    def get_all_fusions(self) -> List[str]:
        query: str = '''SELECT DISTINCT (h_gene || "--" || t_gene) as fusion_pair 
                        FROM tcga_chitars_combined_fusion_information_on_hg19'''
        res = self.select(query)

        return [fusion['fusion_pair'] for fusion in res]
