"""Dragen module"""
from typing import Any, Dict, List, Tuple
from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Dragen(AbstractFusionTool):
    """Dragen tool parser."""

    def parse(self, line, delimiter='\t') -> Tuple[str, Dict[str, Any]]:
        col: List[str] = line.strip().split(delimiter)
        fusion: str = f'{col[0]}'
        details: Dict[str, Any] = {
            'position': f'{col[2]}#{col[3]}'.replace('chr', ''),
            'score': int(col[1]),
        }

        return fusion, details
