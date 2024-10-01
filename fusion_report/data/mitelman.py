"""Mitelman Database"""
from typing import List

from fusion_report.common.db import Db
from fusion_report.common.singleton import Singleton
from fusion_report.settings import Settings


class MitelmanDB(Db, metaclass=Singleton):
    """Implementation of Mitelman Database. All core functionality is handled by parent class."""

    def __init__(self, path: str) -> None:
        super().__init__(path, Settings.MITELMAN["NAME"], Settings.MITELMAN["SCHEMA"])

    def get_all_fusions(self) -> List[str]:
        """Returns all fusions from database."""
        query: str = (
            '''SELECT DISTINCT geneshort FROM mbca WHERE geneshort LIKE "%::%"'''
        )
        res = self.select(query)

        return [fusion["geneshort"].strip().replace("::", "--") for fusion in res]
