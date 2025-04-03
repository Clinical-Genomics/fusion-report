"""Star-Fusion module."""
from typing import Any, Dict, List, Optional, Tuple

from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Starfusion(AbstractFusionTool):
    """Star-Fusion tool parser."""

    def set_header(self, header: str, delimiter: str | None = "\t"):
        self.header: List[str] = header.strip().split(delimiter)

    def parse(self, line: str, delimiter: str | None = "\t") -> List[Tuple[str, Dict[str, Any]]]:
        col: List[str] = [x.strip() for x in line.split(delimiter)]
        fusion: str = f"{col[self.header.index('#FusionName')]}"
        details: Dict[str, Any] = {
            "position": "#".join(
                [
                    col[self.header.index("LeftBreakpoint")],
                    col[self.header.index("RightBreakpoint")],
                ]
            ),
            "junction_reads": int(col[self.header.index("JunctionReadCount")]),
            "spanning_reads": int(col[self.header.index("SpanningFragCount")]),
            "ffmp": float(col[self.header.index("FFPM")]),
        }

        return [(fusion, details)]
