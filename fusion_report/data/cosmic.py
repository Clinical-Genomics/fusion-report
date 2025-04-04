"""Cosmic Database"""

import re

from typing import List

from fusion_report.common.db import Db
from fusion_report.common.singleton import Singleton
from fusion_report.settings import Settings


class CosmicDB(Db, metaclass=Singleton):
    """Implementation of Cosmic Database. All core functionality is handled by parent class."""

    def __init__(self, path: str) -> None:
        super().__init__(path, Settings.COSMIC["NAME"], Settings.COSMIC["SCHEMA"])

    def get_all_fusions(self) -> List[str]:
        """Returns all fusions from database."""
        query: str = '''SELECT DISTINCT
                            FIVE_PRIME_GENE_SYMBOL || '--' || THREE_PRIME_GENE_SYMBOL AS fusion_pair
                        FROM cosmic_fusion_v101_grch38
                        WHERE fusion_pair != ""'''
        res = self.select(query)

        return [
            "--".join(re.findall(r"\(.*?\)", x["fusion_pair"])).replace("(", "").replace(")", "")
            for x in res
        ]
