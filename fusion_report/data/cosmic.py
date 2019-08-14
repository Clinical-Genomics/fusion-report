import os
import re
from typing import List
from fusion_report.common.db import Db
from fusion_report.common.singleton import Singleton


class CosmicDB(Db, metaclass=Singleton):

    def __init__(self, path):
        super().__init__(path, 'COSMIC', 'Cosmic.sql')

    def get_all_fusions(self) -> List[str]:
        query: str = '''SELECT DISTINCT translocation_name FROM CosmicFusionExport
                        WHERE translocation_name != ""'''
        res = self.select(query)

        return ['--'.join(re.findall(r'[A-Z0-9]+(?=\{)', x['translocation_name'])) for x in res]
