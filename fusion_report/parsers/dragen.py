"""Dragen module"""
from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Dragen(AbstractFusionTool):
    """Dragen tool parser."""

    def parse(self, line, delimiter='\t'):
        col = line.strip().split(delimiter)
        fusion = f'{col[0]}'
        details = {
            'position': f'{col[2]}#{col[3]}'.replace('chr', ''),
            'score': int(col[1]),
        }

        return fusion, details
