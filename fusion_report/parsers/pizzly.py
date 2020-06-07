"""Pizzly module"""
from typing import Any, Dict, List, Tuple

from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Pizzly(AbstractFusionTool):
    """Pizzly tool parser."""

    def parse(self, line, delimiter='\t') -> Tuple[str, Dict[str, Any]]:
        col: List[str] = line.strip().split(delimiter)
        fusion: str = f"{col[0]}--{col[2]}"
        details: Dict[str, Any] = {
            'pair_count': int(col[4]),
            'split_count': int(col[5])
        }

        return fusion, details
