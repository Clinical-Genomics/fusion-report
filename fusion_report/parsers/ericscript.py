"""EricScript module"""
from typing import Any, Dict, List, Optional, Tuple

from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Ericscript(AbstractFusionTool):
    """EricScript tool parser."""

    def set_header(self, header: str, delimiter: Optional[str] = '\t'):
        self.header: List[str] = header.strip().split(delimiter)

    def parse(self, line: str, delimiter: Optional[str] = '\t') -> List[Tuple[str, Dict[str, Any]]]:
        col: List[str] = [x.strip() for x in line.split(delimiter)]
        fusion: str = "--".join([
            col[self.header.index('GeneName1')],
            col[self.header.index('GeneName2')]
        ])
        details: Dict[str, Any] = {
            'position': (
                f"{col[self.header.index('chr1')]}:{col[self.header.index('Breakpoint1')]}:"
                f"{col[self.header.index('strand1')]}#{col[self.header.index('chr2')]}:"
                f"{col[self.header.index('Breakpoint2')]}:{col[self.header.index('strand2')]}"
            ),
            'discordant_reads': int(col[self.header.index('crossingreads')]),
            'junction_reads': int(col[self.header.index('spanningreads')]),
            'fusion_type': col[self.header.index('fusiontype')],
            'gene_expr1': float(col[self.header.index('GeneExpr1')]),
            'gene_expr2': float(col[self.header.index('GeneExpr2')]),
            'gene_expr_fusion': float(col[self.header.index('GeneExpr_Fused')])
        }

        return [(fusion, details)]
