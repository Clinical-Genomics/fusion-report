"""FusionGDB Database"""
from typing import List

from fusion_report.common.db import Db
from fusion_report.common.singleton import Singleton
from fusion_report.settings import Settings


class FusionGDB(Db, metaclass=Singleton):
    """Implementation of FusionGDB Database. All core functionality is handled by parent class."""

    def __init__(self, path: str) -> None:
        super().__init__(path, Settings.FUSIONGDB["NAME"], Settings.FUSIONGDB["SCHEMA"])

    def setup(
        self, files: List[str], delimiter: str = "", skip_header=False, encoding="utf-8"
    ):
        super().setup(files, delimiter)

        # fixing embarrassing typo: https://github.com/nf-core/rnafusion/issues/82
        sql = '''UPDATE tcga_chitars_combined_fusion_orf_analyzed_gencode_h19v19
                 SET orf = "Frame-shift" WHERE orf = "Frame-shit"'''
        self.execute(sql)

    def get_all_fusions(self) -> List[str]:
        """Returns all fusions from database."""
        query: str = """SELECT DISTINCT (h_gene || "--" || t_gene) as fusion_pair
                        FROM tcga_chitars_combined_fusion_information_on_hg19"""
        res = self.select(query)

        return [
            fusion.get("fusion_pair").strip().replace("/", "--")
            for fusion in res
            if fusion.get("fusion_pair")
        ]
