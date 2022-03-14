"""Cosmic Database"""
import re

from typing import List

from fusion_report.common.db import Db
from fusion_report.common.singleton import Singleton
from fusion_report.settings import Settings


class CosmicDB(Db, metaclass=Singleton):
    """Implementation of Cosmic Database. All core functionality is handled by parent class."""

    def __init__(self, path: str) -> None:
        super().__init__(path, Settings.COSMIC['NAME'], Settings.COSMIC['SCHEMA'])

    def get_all_fusions(self) -> List[str]:
        """Returns all fusions from database."""
        query: str = '''SELECT DISTINCT translocation_name
                        FROM cosmicfusionexport
                        WHERE translocation_name != ""'''
        res = self.select(query)

        return ['--'.join(re.findall(r'\(.*?\)', x['translocation_name']))
                .replace('(', '').replace(')', '') for x in res]
