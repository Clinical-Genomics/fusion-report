"""FusionCatcher module"""
from typing import Any, Dict, List, Optional, Tuple

from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Fusioncatcher(AbstractFusionTool):
    """FusionCatcher tool parser."""

    def set_header(self, header: str, delimiter: Optional[str] = "\t"):
        self.header: List[str] = header.strip().split(delimiter)

    def parse(
        self, line: str, delimiter: Optional[str] = "\t"
    ) -> List[Tuple[str, Dict[str, Any]]]:
        col: List[str] = [x.strip() for x in line.split(delimiter)]
        fusion: str = "--".join(
            [
                col[self.header.index("Gene_1_symbol(5end_fusion_partner)")],
                col[self.header.index("Gene_2_symbol(3end_fusion_partner)")],
            ]
        )
        details: Dict[str, Any] = {
            "position": "#".join(
                [
                    col[
                        self.header.index(
                            "Fusion_point_for_gene_1(5end_fusion_partner)"
                        )
                    ],
                    col[
                        self.header.index(
                            "Fusion_point_for_gene_2(3end_fusion_partner)"
                        )
                    ],
                ]
            ),
            "common_mapping_reads": int(
                col[self.header.index("Counts_of_common_mapping_reads")]
            ),
            "spanning_pairs": int(col[self.header.index("Spanning_pairs")]),
            "spanning_unique_reads": int(
                col[self.header.index("Spanning_unique_reads")]
            ),
            "longest_anchor": int(col[self.header.index("Longest_anchor_found")]),
            "fusion_type": col[self.header.index("Predicted_effect")].strip(),
        }

        return [(fusion, details)]
