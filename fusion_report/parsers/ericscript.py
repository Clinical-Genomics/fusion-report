"""EricScript module"""
from typing import Any, Dict, List, Tuple
from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Ericscript(AbstractFusionTool):
    """EricScript tool parser."""

    def parse(self, line, delimiter='\t') -> Tuple[str, Dict[str, Any]]:
        col: List[str] = line.strip().split(delimiter)
        fusion: str = f"{col[0]}--{col[1]}"
        details: Dict[str, Any] = {
            'position': f"{col[2]}:{col[3]}:{col[4]}#{col[5]}:{col[6]}:{col[7]}",
            'discordant_reads': int(col[10]),
            'junction_reads': int(col[11]),
            'fusion_type': col[14],
            'gene_expr1': float(col[18]),
            'gene_expr2': float(col[19]),
            'gene_expr_fusion': float(col[20])
        }

        return fusion, details
