import os
import re
from typing import Dict, List


class Settings:
    ROOT_DIR: str = os.path.dirname(os.path.abspath(__file__))
    DATE_FORMAT: str = "%d/%m/%Y"
    THREAD_NUM: int = 2
    VERSION: str = "4.1.4"
    FUSION_WEIGHTS: Dict[str, float] = {
        "cosmic": 0.50,
        "mitelman": 0.50,
        "fusiongdb2": 0.0,
    }

    COSMIC: Dict[str, str] = {
        "NAME": "COSMIC",
        "HOSTNAME": "https://cancer.sanger.ac.uk/api/mono/products/v1/downloads/scripted",
        "SCHEMA": "Cosmic.sql",
        "VERSION": "v101",
        "TARFILE": "Cosmic_Fusion_Tsv_v101_GRCh38.tar",
        "FILE": "Cosmic_Fusion_v101_GRCh38.tsv.gz",
        "HOMEPAGE": "https://cancer.sanger.ac.uk/cosmic/fusion",
    }

    FUSIONGDB2: Dict[str, str] = {
        "NAME": "FusionGDB2",
        "SCHEMA": "FusionGDB2.sql",
        "HOSTNAME": "https://compbio.uth.edu/FusionGDB/combined_tables",
        "FILE": "combinedFGDB2genes_genes_ID_04302024.txt",
        "VERSION": "04302024",
        # The dataset is frozen, so every mirror must serve exactly this file.
        "SHA256": "c09b637b17e461d66cec869d8f083049647a5ee1a34d438d88df2af57d53278f",
        "HOMEPAGE": "https://compbio.uth.edu/FusionGDB2/",
    }

    MITELMAN: Dict[str, str] = {
        "NAME": "Mitelman",
        "SCHEMA": "Mitelman.sql",
        "HOSTNAME": "https://storage.googleapis.com/mitelman-data-files/prod",
        "FILE": "mitelman_db.zip",
        "VERSION": "latest",
        "HOMEPAGE": "https://mitelmandatabase.isb-cgc.org/",
    }

    # Additional download URLs per source, tried in order after the primary URL.
    MIRRORS: Dict[str, List[str]] = {
        "cosmic": [],
        "mitelman": [],
        "fusiongdb2": [],
    }

    @classmethod
    def use_cosmic_version(cls, version: str) -> None:
        """Select the COSMIC release to download (e.g. "v101", the default).

        Only the file names change; the database keeps its internal table name, and the file's
        header is validated against the schema when the database is built.
        """
        if not re.fullmatch(r"v\d+", version or ""):
            raise ValueError(f"invalid COSMIC version '{version}', expected e.g. 'v101'")
        cls.COSMIC["VERSION"] = version
        cls.COSMIC["TARFILE"] = f"Cosmic_Fusion_Tsv_{version}_GRCh38.tar"
        cls.COSMIC["FILE"] = f"Cosmic_Fusion_{version}_GRCh38.tsv.gz"
