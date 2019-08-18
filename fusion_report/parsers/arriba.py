"""Arriba module"""
from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Arriba(AbstractFusionTool):
    """Arriba tool parser."""

    def parse(self, line, delimiter='\t'):
        col = line.strip().split(delimiter)
        fusion = f"{col[0]}--{col[1]}"
        details = {
            'position': f"{col[4]}#{col[5]}",
            'reading-frame': f'{col[21]}',
            'type': f'{col[8]}',
            'split_reads1': f'{col[11]}',
            'split_reads2': f'{col[12]}',
            'discordant_mates': f'{col[13]}',
            'coverage1': f'{col[14]}',
            'coverage2': f'{col[15]}',
            'confidence': f'{col[16]}',
        }

        return fusion, details
