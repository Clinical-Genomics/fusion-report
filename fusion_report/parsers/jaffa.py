"""Jaffa module"""

import re
from typing import Any, Dict, List, Optional, Tuple

from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Jaffa(AbstractFusionTool):
    """Jaffa tool parser."""

    def set_header(self, header: str, delimiter: str | None = ",") -> None:
        self.header: List[str] = header.strip().split(delimiter)

    def _value(self, col: List[str], *keys: str, default: str = "") -> str:
        """Return first matching column value for provided keys."""
        for key in keys:
            if key in self.header:
                index = self.header.index(key)
                if index < len(col):
                    return col[index].strip()
        return default

    @staticmethod
    def _is_true(value: str) -> bool:
        return value.strip().lower() in {"yes", "true", "1", "y"}

    @staticmethod
    def _parse_fusion(fusion_genes: str) -> str:
        """Normalize JAFFA fusion separators and return GENE1--GENE2 format."""
        parts = [x.strip() for x in re.split(r"::|:", fusion_genes) if x.strip()]
        if len(parts) >= 2:
            return f"{parts[0]}--{parts[1]}"
        return fusion_genes.strip().replace("::", "--").replace(":", "--")

    def parse(
        self, line: str, delimiter: Optional[str] = ","
    ) -> List[Tuple[str, Dict[str, Any]]]:
        col: List[str] = [x.strip() for x in line.split(delimiter)]

        fusion: str = self._parse_fusion(col[self.header.index("fusion genes")])

        known: str = self._value(col, "known")
        known_mitelman: str = self._value(col, "known mitelman")
        known_cosmic: str = self._value(col, "known cosmic")
        cosmic_tier: str = self._value(col, "cosmic tier")
        gtex_samples: str = self._value(col, "gtex samples")
        gene_counts_1: str = self._value(col, "geneCounts1")
        gene_counts_2: str = self._value(col, "geneCounts2")

        if not known and (known_mitelman or known_cosmic):
            known = "Yes" if self._is_true(known_mitelman) or self._is_true(known_cosmic) else "No"

        details: Dict[str, Any] = {
            "position": "#".join(
                [
                    ":".join(
                        [
                            col[self.header.index("chrom1")],
                            col[self.header.index("base1")],
                            col[self.header.index("strand1")],
                        ]
                    ).replace("chr", ""),
                    ":".join(
                        [
                            col[self.header.index("chrom2")],
                            col[self.header.index("base2")],
                            col[self.header.index("strand2")],
                        ]
                    ).replace("chr", ""),
                ]
            ),
            "spanning_pairs": int(col[self.header.index("spanning pairs")]),
            "spanning_reads": int(col[self.header.index("spanning reads")]),
            "inframe": col[self.header.index("inframe")].strip(),
            "aligns": col[self.header.index("aligns")].strip(),
            "rearrangement": col[self.header.index("rearrangement")].strip(),
            "classification": col[self.header.index("classification")].strip(),
            "known": known,
        }

        if gene_counts_1:
            details["geneCounts1"] = gene_counts_1
        if gene_counts_2:
            details["geneCounts2"] = gene_counts_2
        if known_mitelman:
            details["known_mitelman"] = known_mitelman
        if known_cosmic:
            details["known_cosmic"] = known_cosmic
        if cosmic_tier:
            details["cosmic_tier"] = cosmic_tier
        if gtex_samples:
            details["gtex_samples"] = gtex_samples

        return [(fusion, details)]
