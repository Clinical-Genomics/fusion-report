from typing import List

from fusion_report.common.db import Db
from fusion_report.common.singleton import Singleton


class MitelmanDB(Db, metaclass=Singleton):

    def __init__(self, path):
        super().__init__(path, 'Mitelman', 'mitelman.sql')

    def get_all_fusions(self) -> List[str]:
        query: str = 'SELECT DISTINCT geneshort FROM molbiolclinassoc WHERE geneshort LIKE "%/%"'
        res = self.select(query)

        return [fusion['geneshort'].strip().replace('/', '--') for fusion in res]
