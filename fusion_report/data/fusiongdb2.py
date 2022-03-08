"""FusionGDB Database"""
import re
from typing import List

from fusion_report.common.db import Db
from fusion_report.common.singleton import Singleton
from fusion_report.settings import Settings


class FusionGDB2(Db, metaclass=Singleton):
    """Implementation of FusionGDB Database. All core functionality is handled by parent class."""

    def __init__(self, path: str) -> None:
        super().__init__(path, Settings.FUSIONGDB2['NAME'], Settings.FUSIONGDB2['SCHEMA'])

    def get_all_fusions(self) -> List[str]:
        """Returns all fusions from database."""
        query: str = '''SELECT DISTINCT fusions
                        FROM fusiongdb2'''
        res = self.select(query)

        return [fusion['fusions'].strip() for fusion in res]
