"""Create databases from local files"""

import glob
import os
import shutil
import time
from argparse import Namespace
from typing import List

from fusion_report.common import db_builders
from fusion_report.common.exceptions.db import DbException
from fusion_report.common.logger import Logger
from fusion_report.common.manifest import OK, Manifest
from fusion_report.data.sources import get_source

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

        original_cwd = os.getcwd()
        tmp_dir = os.path.join(output_path, "tmp_dir")
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        os.chdir(tmp_dir)

        return_err: List[str] = []
        self.manifest = Manifest("createdb")

        try:
            if cosmic_path:
                self.build_cosmic(cosmic_path, return_err)

            if mitelman_path:
                self.build_mitelman(mitelman_path, return_err)

            if fusiongdb2_path:
                self.build_fusiongdb2(fusiongdb2_path, return_err)

            if return_err:
                for err in return_err:
                    LOG.error(err)
                raise DbException("\n".join(return_err))

            self._timestamp(output_path)
            LOG.info("Database creation finished")
        finally:
            # Always move the databases that were built and remove the temporary directory,
            # using absolute paths so this works regardless of the working directory.
            os.chdir(original_cwd)
            self._clean(tmp_dir, output_path)
            if any(s["status"] == OK for s in self.manifest.data["sources"].values()):
                self.manifest.write(output_path)

    def _build(self, key: str, builder, file_path: str, return_err: List[str]) -> None:
        source = get_source(key)
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"{source.name} file not found: {file_path}")
            LOG.info(f"Building {source.name} database from {file_path}")
            rows = builder(file_path)
            self.manifest.record_file(source, file_path, f"file:{file_path}", rows)
            LOG.info(f"{source.name} database created successfully ({rows} rows)")
        except Exception as ex:
            return_err.append(f"{source.name}: {ex}")

    def build_cosmic(self, file_path: str, return_err: List[str]) -> None:
        """Build COSMIC database from a local TSV file (plain or gzipped)."""
        self._build("cosmic", db_builders.build_cosmic, file_path, return_err)

    def build_mitelman(self, file_path: str, return_err: List[str]) -> None:
        """Build Mitelman database from a ZIP archive or extracted data file."""
        self._build("mitelman", db_builders.build_mitelman, file_path, return_err)

    def build_fusiongdb2(self, file_path: str, return_err: List[str]) -> None:
        """Build FusionGDB2 database from a TSV or pre-processed CSV file."""
        self._build("fusiongdb2", db_builders.build_fusiongdb2, file_path, return_err)

    @staticmethod
    def _clean(tmp_dir: str, output_dir: str):
        """Move generated .db files to output dir and remove temp directory."""
        for temp in glob.glob(os.path.join(tmp_dir, "*.db")):
            shutil.copy(temp, output_dir)
        shutil.rmtree(tmp_dir, ignore_errors=True)

    @staticmethod
    def _timestamp(output_dir: str):
        """Create a timestamp file at DB creation."""
        timestr = time.strftime("%Y-%m-%d/%H:%M")
        with open(os.path.join(output_dir, "DB-timestamp.txt"), "w") as text_file:
            text_file.write(timestr)
