import os
import re
from typing import List
from fusion_report.common.db import Db
from fusion_report.common.singleton import Singleton

class CosmicDB(Db, metaclass=Singleton):

    def __init__(self, path):
        self.name = 'COSMIC'
        self.schema = 'Cosmic.sql'
        self.__connection = self.connect(path, 'cosmic.db')

    def setup(self):
        try:
            with open(self.schema, 'r', encoding='utf-8') as f:
                self.__connection.execute(f.read())
        except Exception as ex:
            raise ex

    def get_all_fusions(self) -> List[str]:
        query: str = '''SELECT DISTINCT translocation_name FROM CosmicFusionExport
                        WHERE translocation_name != ""'''
        res = Db().select(self.__connection, query)

        return ['--'.join(re.findall(r'[A-Z0-9]+(?=\{)', x['translocation_name'])) for x in res]
