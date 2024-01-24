# Replace Test with the name of the new tool
"""starseqr module"""
from typing import Any, Dict, List, Tuple

from typing import Any, Dict, List, Optional, Tuple

from fusion_report.parsers.abstract_fusion import AbstractFusionTool

class Starseqr(AbstractFusionTool):
    """starseqr tool parser."""

    def set_header(self, header: str, delimiter: Optional[str] = '\t'):
        self.header: List[str] = header.strip().split(delimiter)

    def parse(self, line: str, delimiter: Optional[str] = '\t') -> List[Tuple[str, Dict[str, Any]]]:
        col: List[str] = line.strip().split(delimiter)
       	fusion: str = f'{col[0]}' 
        details: Dict[str, Any] = {
            'position': f'{col[6]}#{col[7]}'.replace('chr', ''),
            'NREAD_SPANS': col[self.header.index('NREAD_SPANS')],
            'NREAD_JXNLEFT': col[self.header.index('NREAD_JXNLEFT')],
            'NREAD_JXNRIGHT': col[self.header.index('NREAD_JXNRIGHT')]
        }

        return [(fusion, details)]

