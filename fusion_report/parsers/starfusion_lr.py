"""Star-Fusion Long Reads module."""

from typing import Any, Dict, List, Optional, Tuple
from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Starfusion_lr(AbstractFusionTool):
    """Star-Fusion Long Reads (Nanopore or PacBio) tool parser."""

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
            "num_LR": int(col[self.header.index("num_LR")]),
            "ffmp": float(col[self.header.index("LR_FFPM")]),
        }

        return [(fusion, details)]
