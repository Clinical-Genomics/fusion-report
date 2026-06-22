import os
from typing import Dict


class Settings:
    ROOT_DIR: str = os.path.dirname(os.path.abspath(__file__))
    DATE_FORMAT: str = "%d/%m/%Y"
    THREAD_NUM: int = 2
    VERSION: str = "4.1.2"
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
    }

    FUSIONGDB2: Dict[str, str] = {
        "NAME": "FusionGDB2",
        "SCHEMA": "FusionGDB2.sql",
        "HOSTNAME": "https://compbio.uth.edu/FusionGDB/combined_tables",
        "FILE": "combinedFGDB2genes_genes_ID_04302024.txt",
    }

    MITELMAN: Dict[str, str] = {
        "NAME": "Mitelman",
        "SCHEMA": "Mitelman.sql",
        "HOSTNAME": "https://storage.googleapis.com/mitelman-data-files/prod",
        "FILE": "mitelman_db.zip",
    }
