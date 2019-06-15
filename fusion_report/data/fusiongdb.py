import os
from typing import List
from fusion_report.common.db import Db
from fusion_report.common.singleton import Singleton

class FusionGDB(Db, metaclass=Singleton):

    def __init__(self, path):
        self.name = 'FusionGDB'
        self.schema = 'FusionGDB.sql'
        self.__connection = self.connect(path, 'fusiongdb.db')

    def setup(self):
        try:
            with open(self.schema, 'r', encoding='utf-8') as f:
                self.__connection.execute(f.read())
        except Exception as ex:
            raise ex

    def get_all_fusions(self) -> List[str]:
        query: str = '''SELECT DISTINCT (h_gene || "--" || t_gene) as fusion_pair 
                        FROM TCGA_ChiTaRS_combined_fusion_information_on_hg19'''
        res = Db().select(self.__connection, query)

        return [fusion['fusion_pair'] for fusion in res]
