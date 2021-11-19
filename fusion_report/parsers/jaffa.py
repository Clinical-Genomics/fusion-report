"""Jaffa module"""
from typing import Any, Dict, List, Optional, Tuple
from fusion_report.parsers.abstract_fusion import AbstractFusionTool
import csv

class Jaffa(AbstractFusionTool):
    """Jaffa tool parser."""

    def set_header(self, header: str, delimiter: Optional[str] = ','):

        self.header: List[str] = header.strip().split(delimiter)

    def parse(self, line: str, delimiter: Optional[str] = ',') -> List[Tuple[str, Dict[str, Any]]]:
        
        #print(self.header)

        col: List[str] = [x.strip() for x in line.split(delimiter)]

        #print(type(col[self.header.index('fusion.genes')]))
        #print(type(col[self.header.index('fusion.genes')].split(':')))
        
        fusions = col[self.header.index('fusion genes')].split(':')

        fusion: str = '--'.join([fusions[0], fusions[1]])

        details: Dict[str, Any] = {
            'position': 

            "#".join([
                ':'.join([col[self.header.index('chrom1')],
                         col[self.header.index('base1')],
                         col[self.header.index('strand1')]
                         ]).replace('chr', ''),
                ':'.join([col[self.header.index('chrom2')],
                         col[self.header.index('base2')],
                         col[self.header.index('strand2')]
                         ]).replace('chr', '')
                ]),
            'spanning_pairs': int(col[self.header.index('spanning pairs')]),
            'spanning_reads': int(col[self.header.index('spanning reads')]),
            'inframe': col[self.header.index('inframe')].strip(),
            'aligns': col[self.header.index('aligns')].strip(),
            'rearrangement': col[self.header.index('rearrangement')].strip(),
            'classification': col[self.header.index('classification')].strip(),
            'known': col[self.header.index('known')].strip()
        }
        
        return [(fusion, details)]