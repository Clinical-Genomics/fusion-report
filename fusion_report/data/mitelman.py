import os
import re
from typing import List
from fusion_report.common.db import Db
from fusion_report.common.singleton import Singleton

class MitelmanDB(Db, metaclass=Singleton):

    def __init__(self, path):
        self.name = 'Mitelman'
        self.schema = 'Mitelman.sql'
        self.__connection = self.connect(path, 'mitelman.db')

    def setup(self):
        try:
            with open(self.schema, 'r', encoding='utf-8') as f:
                self.__connection.execute(f.read())
        except Exception as ex:
            raise ex

    def get_all_fusions(self) -> List[str]:
        query: str = 'SELECT DISTINCT GeneShort FROM MolBiolClinAssoc WHERE GeneShort LIKE "%/%"'
        res = Db().select(self.__connection, query)

        return [fusion['GeneShort'].strip().replace('/', '--') for fusion in res]
