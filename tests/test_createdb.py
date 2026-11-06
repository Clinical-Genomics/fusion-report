"""Unit tests for `createdb` (building databases from local files)."""

from argparse import Namespace
from pathlib import Path

import pytest

from fusion_report.common.exceptions.db import DbException
from fusion_report.createdb import CreateDB
from fusion_report.data.fusiongdb2 import FusionGDB2
from fusion_report.data.mitelman import MitelmanDB

TEST_DATA = Path(__file__).parent / "test_data"


def _params(output, **files):
    values = dict(output=str(output), cosmic=None, mitelman=None, fusiongdb2=None)
    values.update({key: str(value) for key, value in files.items()})
    return Namespace(**values)


def test_createdb_from_fixtures(tmp_path):
    CreateDB(
        _params(
            tmp_path,
            mitelman=TEST_DATA / "mitelman_mini.zip",
            fusiongdb2=TEST_DATA / "fusiongdb2_mini.txt",
        )
    )
    assert "FGFR3--TACC3" in MitelmanDB(str(tmp_path)).get_all_fusions()
    assert "FGFR3--TACC3" in FusionGDB2(str(tmp_path)).get_all_fusions()
    assert (tmp_path / "DB-timestamp.txt").exists()
    assert not (tmp_path / "tmp_dir").exists()


def test_createdb_relative_output_and_cwd_restored(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    CreateDB(_params("db", fusiongdb2=TEST_DATA / "fusiongdb2_mini.txt"))
    assert Path.cwd() == tmp_path
    assert (tmp_path / "db" / "fusiongdb2.db").exists()
    assert not (tmp_path / "db" / "tmp_dir").exists()


def test_createdb_error_keeps_built_dbs_and_cleans_up(tmp_path):
    bad = tmp_path / "bad.txt"
    bad.write_text("only\tthree\tcolumns\n")
    output = tmp_path / "db"

    with pytest.raises(DbException, match="FusionGDB2: unexpected file format"):
        CreateDB(_params(output, mitelman=TEST_DATA / "mitelman_mini.zip", fusiongdb2=bad))

    assert (output / "mitelman.db").exists()
    assert not (output / "fusiongdb2.db").exists()
    assert not (output / "tmp_dir").exists()


def test_createdb_missing_file(tmp_path):
    with pytest.raises(DbException, match="Mitelman file not found"):
        CreateDB(_params(tmp_path / "db", mitelman=tmp_path / "missing.zip"))
