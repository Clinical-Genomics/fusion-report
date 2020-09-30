"""Pizzly module"""
from typing import Any, Dict, List, Tuple

from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Pizzly(AbstractFusionTool):
    """Pizzly tool parser."""

    def set_header(self, header: str, delimiter: str = '\t') -> str:
        self.header: List[str] = header.strip().split(delimiter)

    def parse(self, line: str, delimiter: str = '\t') -> List[Tuple[str, Dict[str, Any]]]:
        col: List[str] = line.strip().split(delimiter)
        fusion: str = f"""
            {col[self.header.index('geneA.name')]}--{col[self.header.index('geneB.name')]}
        """
        details: Dict[str, Any] = {
            'pair_count': int(col[self.header.index('paircount')]),
            'split_count': int(col[self.header.index('splitcount')])
        }

        return [(fusion, details)]
