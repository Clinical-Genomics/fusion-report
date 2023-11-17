"""Dragen module"""
from typing import Any, Dict, List, Optional, Tuple

from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Dragen(AbstractFusionTool):
    """Dragen tool parser."""

    def set_header(self, header: str, delimiter: Optional[str] = "\t"):
        self.header: List[str] = header.strip().split(delimiter)

    def parse(self, line: str, delimiter: Optional[str] = "\t") -> List[Tuple[str, Dict[str, Any]]]:
        col: List[str] = [x.strip() for x in line.split(delimiter)]
        fusion: str = col[self.header.index("#FusionGene")]
        details: Dict[str, Any] = {
            "position": "#".join(
                [
                    col[self.header.index("LeftBreakpoint")],
                    col[self.header.index("RightBreakpoint")],
                ]
            ).replace("chr", ""),
            "score": int(col[self.header.index("Score")]),
        }

        return [(fusion, details)]
