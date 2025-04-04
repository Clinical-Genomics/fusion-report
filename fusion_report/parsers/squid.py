"""Squid module"""

from typing import Any, Dict, List, Optional, Tuple

from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Squid(AbstractFusionTool):
    """Squid tool parser."""

    def set_header(self, header: str, delimiter: str | None = "\t"):
        self.header: List[str] = header.strip().split(delimiter)

    def parse_multiple(self, col: str, delimiter: str) -> List[str]:
        return [fusion.replace(":", "--") for fusion in col.split(delimiter)]

    def parse(self, line: str, delimiter: str | None = "\t") -> List[Tuple[str, Dict[str, Any]]]:
        col: List[str] = [x.strip() for x in line.split(delimiter)]
        if col[self.header.index("Type")].strip() == "non-fusion-gene":
            return [("", {})]

        fusions = self.parse_multiple(col[self.header.index("FusedGenes")], ",")
        left_breakpoint: str = (
            f"{col[self.header.index('# chrom1')]}:{col[self.header.index('start1')]}"
            "-"
            f"{col[self.header.index('end1')]}:{col[self.header.index('strand1')]}"
        ).replace("chr", "")
        right_breakpoint: str = (
            f"{col[self.header.index('chrom2')]}:{col[self.header.index('start2')]}"
            "-"
            f"{col[self.header.index('end2')]}:{col[self.header.index('strand2')]}"
        ).replace("chr", "")
        details: Dict[str, Any] = {
            "position": (
                f"{left_breakpoint}#{right_breakpoint}"
                if col[self.header.index("strand1")] == "+"
                else f"{right_breakpoint}#{left_breakpoint}"
            ),
            "score": int(col[self.header.index("score")]),
        }

        return [(fusion, details) for fusion in fusions]
