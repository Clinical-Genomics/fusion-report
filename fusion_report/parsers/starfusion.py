"""Star-Fusion module."""
from typing import Any, Dict, List, Tuple

from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Starfusion(AbstractFusionTool):
    """Star-Fusion tool parser."""

    def parse(self, line, delimiter='\t') -> Tuple[str, Dict[str, Any]]:
        col: List[str] = line.strip().split(delimiter)
        fusion: str = f"{col[0]}"
        details: Dict[str, Any] = {
            'position': f"{col[5]}#{col[7]}",
            'junction_reads': int(col[1]),
            'spanning_reads': int(col[2]),
            'ffmp': float(col[11])
        }

        return fusion, details
