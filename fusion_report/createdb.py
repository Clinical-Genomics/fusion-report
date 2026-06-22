"""Create databases from local files"""

import gzip
import os
import shutil
import time
from argparse import Namespace
from typing import List
from zipfile import ZipFile

import pandas as pd

from fusion_report.common.exceptions.db import DbException
from fusion_report.common.logger import Logger
from fusion_report.data.cosmic import CosmicDB
from fusion_report.data.fusiongdb2 import FusionGDB2
from fusion_report.data.mitelman import MitelmanDB

LOG = Logger(__name__)


class CreateDB:
    """Build database files from local data files without downloading.

    Supports building any combination of COSMIC, Mitelman, and FusionGDB2
    databases from user-provided files.
    """

    def __init__(self, params: Namespace):
        if not params.cosmic and not params.mitelman and not params.fusiongdb2:
            raise DbException(
                "At least one database file must be provided. "
                "Use --cosmic, --mitelman, and/or --fusiongdb2."
            )

        # Resolve paths to absolute before changing directory
        cosmic_path = os.path.abspath(params.cosmic) if params.cosmic else None
        mitelman_path = os.path.abspath(params.mitelman) if params.mitelman else None
        fusiongdb2_path = os.path.abspath(params.fusiongdb2) if params.fusiongdb2 else None
        output_path = os.path.abspath(params.output)

        if not os.path.exists(output_path):
            os.makedirs(output_path, 0o755)

        tmp_dir = os.path.join(output_path, "tmp_dir")
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        os.chdir(tmp_dir)

        return_err: List[str] = []

        if cosmic_path:
            self.build_cosmic(cosmic_path, return_err)

        if mitelman_path:
            self.build_mitelman(mitelman_path, return_err)

        if fusiongdb2_path:
            self.build_fusiongdb2(fusiongdb2_path, return_err)

        if return_err:
            for err in return_err:
                LOG.error(err)
            raise DbException(return_err)

        # Move db files and clean up
        self._clean()
        self._timestamp(output_path)
        LOG.info("Database creation finished")

    @staticmethod
    def build_cosmic(file_path: str, return_err: List[str]) -> None:
        """Build COSMIC database from a local TSV file (plain or gzipped)."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"COSMIC file not found: {file_path}")

            data_file = file_path
            if file_path.endswith(".gz"):
                LOG.info(f"Decompressing {file_path}")
                decompressed = os.path.basename(file_path).rsplit(".gz", 1)[0]
                with gzip.open(file_path, "rb") as f_in, open(decompressed, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
                data_file = decompressed

            # Rename to match expected table name
            target_file = "cosmic_fusion_v101_grch38.tsv"
            if os.path.basename(data_file) != target_file:
                shutil.copy(data_file, target_file)

            db = CosmicDB(".")
            db.setup([target_file], delimiter="\t", skip_header=True)
            LOG.info("COSMIC database created successfully")
        except Exception as ex:
            return_err.append(f"COSMIC: {ex}")

    @staticmethod
    def build_mitelman(file_path: str, return_err: List[str]) -> None:
        """Build Mitelman database from a ZIP archive or extracted data file."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Mitelman file not found: {file_path}")

            if file_path.endswith(".zip"):
                LOG.info(f"Extracting {file_path}")
                with ZipFile(file_path, "r") as archive:
                    files = [
                        x for x in archive.namelist() if "MBCA.TXT.DATA" in x and "MACOSX" not in x
                    ]
                    archive.extractall()
            else:
                files = [file_path]

            db = MitelmanDB(".")
            db.setup(files, delimiter="\t", skip_header=False, encoding="ISO-8859-1")
            LOG.info("Mitelman database created successfully")
        except Exception as ex:
            return_err.append(f"Mitelman: {ex}")

    @staticmethod
    def build_fusiongdb2(file_path: str, return_err: List[str]) -> None:
        """Build FusionGDB2 database from a TSV or pre-processed CSV file."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"FusionGDB2 file not found: {file_path}")

            if file_path.endswith(".txt"):
                LOG.info(f"Processing FusionGDB2 file {file_path}")
                # Headerless 6-column TSV: col2 = 5'-gene, col4 = 3'-gene (0-indexed)
                df = pd.read_csv(file_path, sep="\t", header=None)
                df["fusion"] = df[2] + "--" + df[4]
                csv_file = "fusionGDB2.csv"
                df["fusion"].to_csv(csv_file, header=False, index=False, sep=",", encoding="utf-8")
            elif file_path.endswith(".csv"):
                csv_file = file_path
            else:
                raise ValueError(
                    f"Unsupported FusionGDB2 file format: {file_path}. " "Expected .txt or .csv"
                )

            db = FusionGDB2(".")
            db.setup([csv_file], delimiter=",", skip_header=False)
            LOG.info("FusionGDB2 database created successfully")
        except Exception as ex:
            return_err.append(f"FusionGDB2: {ex}")

    @staticmethod
    def _clean():
        """Move generated .db files to output dir and remove temp directory."""
        import glob

        for temp in glob.glob("*.db"):
            shutil.copy(temp, "../")
        os.chdir("../")
        shutil.rmtree("tmp_dir")

    @staticmethod
    def _timestamp(output_dir: str):
        """Create a timestamp file at DB creation."""
        timestr = time.strftime("%Y-%m-%d/%H:%M")
        with open(os.path.join(output_dir, "DB-timestamp.txt"), "w") as text_file:
            text_file.write(timestr)
