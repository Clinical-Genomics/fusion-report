"""Unit tests for the shared database builders (format validation)."""

import gzip
import zipfile
from pathlib import Path

import pytest

from fusion_report.common import db_builders
from fusion_report.data.cosmic import CosmicDB
from fusion_report.data.fusiongdb2 import FusionGDB2

TEST_DATA = Path(__file__).parent / "test_data"
COLUMNS = db_builders.cosmic_columns()
COSMIC_HEADER = "\t".join(COLUMNS) + "\n"


def _cosmic_row(sample_id, five, three):
    values = {name: "" for name in COLUMNS}
    values.update(
        COSMIC_SAMPLE_ID=str(sample_id),
        FIVE_PRIME_GENE_SYMBOL=five,
        THREE_PRIME_GENE_SYMBOL=three,
        FIVE_PRIME_GENOME_START_FROM="1",
    )
    return "\t".join(values[name] for name in COLUMNS) + "\n"


@pytest.fixture(autouse=True)
def _in_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def test_mitelman_fixture(tmp_path):
    assert db_builders.build_mitelman(str(TEST_DATA / "mitelman_mini.zip")) == 5
    assert (tmp_path / "mitelman.db").exists()


def test_mitelman_wrong_column_count(tmp_path):
    data = tmp_path / "MBCA.TXT.DATA"
    data.write_text("a\tb\tc\n")
    with pytest.raises(ValueError, match="expected 12 tab-separated columns, got 3"):
        db_builders.build_mitelman(str(data))


def test_mitelman_zip_without_data_file(tmp_path):
    archive = tmp_path / "m.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("README", "x")
    with pytest.raises(ValueError, match="MBCA.TXT.DATA not found"):
        db_builders.build_mitelman(str(archive))


def test_mitelman_corrupt_zip(tmp_path):
    archive = tmp_path / "m.zip"
    archive.write_bytes(b"PK\x03\x04 broken")
    with pytest.raises(ValueError, match="not a valid ZIP archive"):
        db_builders.build_mitelman(str(archive))


def test_fusiongdb2_fixture(tmp_path):
    assert db_builders.build_fusiongdb2(str(TEST_DATA / "fusiongdb2_mini.txt")) == 6
    assert "ETV6--NTRK3" in FusionGDB2(str(tmp_path)).get_all_fusions()


def test_fusiongdb2_preprocessed_csv(tmp_path):
    csv = tmp_path / "fusions.csv"
    csv.write_text("A--B\nC--D\n")
    assert db_builders.build_fusiongdb2(str(csv)) == 2


@pytest.mark.parametrize("content", ["a\tb\tc\td\te\n", "a\tb\tc\td\te\tf\tg\n"])
def test_fusiongdb2_wrong_column_count(tmp_path, content):
    data = tmp_path / "f.txt"
    data.write_text(content)
    with pytest.raises(ValueError, match="expected a headerless 6-column TSV"):
        db_builders.build_fusiongdb2(str(data))


def test_fusiongdb2_empty_and_unsupported(tmp_path):
    empty = tmp_path / "f.txt"
    empty.write_text("")
    with pytest.raises(ValueError, match="empty"):
        db_builders.build_fusiongdb2(str(empty))
    with pytest.raises(ValueError, match="unsupported file format"):
        db_builders.build_fusiongdb2(str(tmp_path / "f.xlsx"))


def test_cosmic_gzipped(tmp_path):
    data = tmp_path / "Cosmic_Fusion_v101_GRCh38.tsv.gz"
    content = COSMIC_HEADER + _cosmic_row(1, "BCR", "ABL1") + _cosmic_row(2, "ETV6", "NTRK3")
    data.write_bytes(gzip.compress(content.encode()))
    assert db_builders.build_cosmic(str(data)) == 2
    assert "BCR--ABL1" in CosmicDB(str(tmp_path)).get_all_fusions()


def test_cosmic_schema_has_25_columns():
    assert len(COLUMNS) == 25
    assert COLUMNS[0] == "COSMIC_SAMPLE_ID" and COLUMNS[-1] == "PUBMED_PMID"


def test_cosmic_wrong_column_count(tmp_path):
    data = tmp_path / "cosmic.tsv"
    data.write_text("ID\tGENE_A\tGENE_B\n1\tBCR\tABL1\n")
    with pytest.raises(ValueError, match="expected 25 COSMIC fusion columns, got 3.*missing"):
        db_builders.build_cosmic(str(data))


def test_cosmic_gene_columns_moved(tmp_path):
    data = tmp_path / "cosmic.tsv"
    data.write_text("\t".join(reversed(COLUMNS)) + "\n")
    with pytest.raises(ValueError, match="expected column FIVE_PRIME_GENE_SYMBOL at position 9"):
        db_builders.build_cosmic(str(data))


def test_cosmic_other_name_differences_only_warn(tmp_path, caplog):
    renamed = ["SAMPLE_ID" if name == "COSMIC_SAMPLE_ID" else name.lower() for name in COLUMNS]
    data = tmp_path / "cosmic.tsv"
    data.write_text("\t".join(renamed) + "\n" + _cosmic_row(1, "BCR", "ABL1"))
    assert db_builders.build_cosmic(str(data)) == 1
    assert "differs from the expected columns" in caplog.text


def test_cosmic_corrupt_gzip_and_no_rows(tmp_path):
    corrupt = tmp_path / "c.tsv.gz"
    corrupt.write_bytes(b"\x1f\x8b broken")
    with pytest.raises(ValueError, match="could not decompress"):
        db_builders.build_cosmic(str(corrupt))

    header_only = tmp_path / "c.tsv"
    header_only.write_text(COSMIC_HEADER)
    with pytest.raises(ValueError, match="no data rows"):
        db_builders.build_cosmic(str(header_only))
