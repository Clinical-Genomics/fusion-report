"""Build the local SQLite databases from source files, with format validation.

Shared by `download` (after fetching a file) and `createdb` (local files), so both paths parse
and validate files the same way. Each builder works in the current directory, writes
`<name>.db` and returns the number of imported rows. Invalid input raises `ValueError` with a
message describing what was expected.
"""

import gzip
import os
import re
import shutil
from typing import List
from zipfile import BadZipFile, ZipFile

import pandas as pd

from fusion_report.common.logger import Logger
from fusion_report.data.cosmic import CosmicDB
from fusion_report.data.fusiongdb2 import FusionGDB2
from fusion_report.data.mitelman import MitelmanDB
from fusion_report.settings import Settings

LOG = Logger(__name__)

MITELMAN_DATA_FILE = "MBCA.TXT.DATA"
MITELMAN_COLUMNS = 12
FUSIONGDB2_COLUMNS = 6
# Internal table name; kept stable so existing databases keep working (see Cosmic.sql).
COSMIC_TABLE_FILE = "cosmic_fusion_v101_grch38.tsv"
COSMIC_KEY_COLUMNS = ("FIVE_PRIME_GENE_SYMBOL", "THREE_PRIME_GENE_SYMBOL")


def cosmic_columns() -> List[str]:
    """Column names of the COSMIC table, in order, as defined in the schema."""
    schema = os.path.join(Settings.ROOT_DIR, "data", "schema", Settings.COSMIC["SCHEMA"])
    with open(schema, "r", encoding="utf-8") as handle:
        return re.findall(r'^\s*"(\w+)"\s+\w', handle.read(), flags=re.MULTILINE)


def _check_cosmic_header(header: List[str], data_file: str) -> None:
    """Rows are imported by position: require the schema's column count and the gene symbol
    columns at their schema positions. Other naming differences are only logged."""
    expected = cosmic_columns()
    name = os.path.basename(data_file)
    if len(header) != len(expected):
        missing = [column for column in COSMIC_KEY_COLUMNS if column not in header]
        hint = f" (missing: {', '.join(missing)})" if missing else ""
        raise ValueError(
            f"unexpected file format in {name}: expected {len(expected)} COSMIC fusion columns, "
            f"got {len(header)}{hint}"
        )
    for column in COSMIC_KEY_COLUMNS:
        position = expected.index(column)
        if header[position] != column:
            raise ValueError(
                f"unexpected file format in {name}: expected column {column} at position "
                f"{position + 1}, found {header[position]}"
            )
    if header != expected:
        LOG.warning(
            f"COSMIC: the header of {name} differs from the expected columns; importing by "
            "position."
        )


def count_rows(path: str, encoding: str = "utf-8", skip_header: bool = False) -> int:
    with open(path, "r", encoding=encoding) as handle:
        count = sum(1 for line in handle if line.strip())
    return count - 1 if skip_header and count else count


def build_mitelman(file_path: str) -> int:
    """Build mitelman.db from the Mitelman ZIP archive or an extracted MBCA.TXT.DATA file."""
    if file_path.endswith(".zip"):
        try:
            with ZipFile(file_path, "r") as archive:
                files = [
                    x for x in archive.namelist() if MITELMAN_DATA_FILE in x and "MACOSX" not in x
                ]
                if not files:
                    raise ValueError(f"{MITELMAN_DATA_FILE} not found in the archive")
                archive.extractall()
        except BadZipFile as ex:
            raise ValueError(f"not a valid ZIP archive: {ex}") from ex
    else:
        files = [file_path]

    rows = 0
    for data_file in files:
        with open(data_file, "r", encoding="ISO-8859-1") as handle:
            columns = len(handle.readline().rstrip("\n").split("\t"))
        if columns != MITELMAN_COLUMNS:
            raise ValueError(
                f"unexpected file format in {os.path.basename(data_file)}: expected "
                f"{MITELMAN_COLUMNS} tab-separated columns, got {columns}"
            )
        rows += count_rows(data_file, encoding="ISO-8859-1")
    if rows == 0:
        raise ValueError("the Mitelman data file is empty")

    MitelmanDB(".").setup(files, delimiter="\t", skip_header=False, encoding="ISO-8859-1")
    return rows


def build_fusiongdb2(file_path: str) -> int:
    """Build fusiongdb2.db from the headerless 6-column TSV (.txt) or a pre-processed CSV."""
    # The table name is derived from the file name, so always import from fusionGDB2.csv
    csv_file = "fusionGDB2.csv"
    if file_path.endswith(".csv"):
        if os.path.abspath(file_path) != os.path.abspath(csv_file):
            shutil.copy(file_path, csv_file)
    elif file_path.endswith((".txt", ".tsv")):
        try:
            df = pd.read_csv(file_path, sep="\t", header=None)
        except pd.errors.EmptyDataError as ex:
            raise ValueError("the FusionGDB2 file is empty") from ex
        if df.shape[1] != FUSIONGDB2_COLUMNS or df.empty:
            raise ValueError(
                f"unexpected file format: expected a headerless {FUSIONGDB2_COLUMNS}-column TSV, "
                f"got {df.shape[1]} column(s) and {len(df)} row(s)"
            )
        # col2 = 5'-gene, col4 = 3'-gene (0-indexed)
        df["fusion"] = df[2].astype(str) + "--" + df[4].astype(str)
        df["fusion"].to_csv(csv_file, header=False, index=False, sep=",", encoding="utf-8")
    else:
        raise ValueError(f"unsupported file format: {file_path}. Expected .txt or .csv")

    rows = count_rows(csv_file)
    if rows == 0:
        raise ValueError("the FusionGDB2 file is empty")
    FusionGDB2(".").setup([csv_file], delimiter=",", skip_header=False)
    return rows


def build_cosmic(file_path: str) -> int:
    """Build cosmic.db from the COSMIC fusion TSV (plain or gzipped)."""
    data_file = file_path
    if file_path.endswith(".gz"):
        data_file = os.path.basename(file_path).rsplit(".gz", 1)[0]
        try:
            with gzip.open(file_path, "rb") as f_in, open(data_file, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        except (OSError, EOFError) as ex:
            raise ValueError(f"could not decompress {os.path.basename(file_path)}: {ex}") from ex

    with open(data_file, "r", encoding="utf-8") as handle:
        header: List[str] = handle.readline().rstrip("\n").split("\t")
    _check_cosmic_header([column.strip().upper() for column in header], data_file)

    if os.path.abspath(data_file) != os.path.abspath(COSMIC_TABLE_FILE):
        # copy + replace also works on case-insensitive file systems, where the source and
        # the table file only differ in case
        shutil.copy(data_file, f"{COSMIC_TABLE_FILE}.tmp")
        os.replace(f"{COSMIC_TABLE_FILE}.tmp", COSMIC_TABLE_FILE)
    rows = count_rows(COSMIC_TABLE_FILE, skip_header=True)
    if rows == 0:
        raise ValueError("the COSMIC file has no data rows")
    CosmicDB(".").setup([COSMIC_TABLE_FILE], delimiter="\t", skip_header=True)
    return rows
