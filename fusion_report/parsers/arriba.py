"""Arriba module"""
from typing import Any, Dict, List, Tuple

from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Arriba(AbstractFusionTool):
    """Arriba tool parser."""

    def parse_multiple(self, left_fusion: str, right_fusion: str, delimiter: str) -> List[str]:
        if delimiter not in left_fusion and delimiter not in right_fusion:
            return [f'{left_fusion}--{right_fusion}']

        left: List[str] = [x.split('(')[0] for x in left_fusion.split(delimiter)]
        right: List[str] = [x.split('(')[0] for x in right_fusion.split(delimiter)]
        fusions = [f'{a}--{b}' for a in left for b in right]

        return fusions

    def parse(self, line, delimiter='\t') -> List[Tuple[str, Dict[str, Any]]]:
        col: List[str] = line.strip().split(delimiter)
        fusions = self.parse_multiple(col[0], col[1], ',')
        details: Dict[str, Any] = {
            'position': f"{col[4]}#{col[5]}",
            'reading-frame': f'{col[21]}',
            'type': f'{col[8]}',
            'split_reads1': f'{col[11]}',
            'split_reads2': f'{col[12]}',
            'discordant_mates': f'{col[13]}',
            'coverage1': f'{col[14]}',
            'coverage2': f'{col[15]}',
            'confidence': f'{col[16]}',
        }

        return [(fusion, details) for fusion in fusions]
