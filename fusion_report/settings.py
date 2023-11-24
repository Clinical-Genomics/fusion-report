import os

from typing import Any, Dict


class Settings:
    ROOT_DIR: str = os.path.dirname(os.path.abspath(__file__))
    VERSION: str = "2.1.5"
    DATE_FORMAT: str = "%d/%m/%Y"
    THREAD_NUM: int = 2
    FUSION_WEIGHTS: Dict[str, float] = {
        "cosmic": 0.50,
        "mitelman": 0.50,
        "fusiongdb2": 0.0,
    }

    COSMIC: Dict[str, str] = {
        "NAME": "COSMIC",
        "HOSTNAME": "https://cancer.sanger.ac.uk/cosmic/file_download/GRCh38/cosmic/v98",
        "SCHEMA": "Cosmic.sql",
        "FILE": "CosmicFusionExport.tsv.gz",
    }

    FUSIONGDB2: Dict[str, str] = {
        "NAME": "FusionGDB2",
        "SCHEMA": "FusionGDB2.sql",
        "HOSTNAME": "https://compbio.uth.edu/FusionGDB2/tables",
        "FILE": "FusionGDB2_id.xlsx",
    }

    MITELMAN: Dict[str, str] = {
        "NAME": "Mitelman",
        "SCHEMA": "Mitelman.sql",
        "HOSTNAME": "https://storage.googleapis.com/mitelman-data-files/prod",
        "FILE": "mitelman_db.zip",
    }
