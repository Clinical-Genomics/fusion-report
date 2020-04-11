"""FusionCatcher module"""
from typing import Any, Dict, List, Tuple
from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Fusioncatcher(AbstractFusionTool):
    """FusionCatcher tool parser."""

    def parse(self, line, delimiter='\t') -> Tuple[str, Dict[str, Any]]:
        col: List[str] = line.strip().split(delimiter)
        fusion: str = f"{col[0]}--{col[1]}"
        details: Dict[str, Any] = {
            'position': f"{col[8]}#{col[9]}",
            'common_mapping_reads': int(col[3]),
            'spanning_pairs': int(col[4]),
            'spanning_unique_reads': int(col[5]),
            'longest_anchor': int(col[6]),
            'fusion_type': col[15].strip()
        }

        return fusion, details
