"""Unit tests for the command-line entrypoint and argument parsing."""

import sys
from pathlib import Path

import pytest

from fusion_report.args_builder import ArgsBuilder
from fusion_report.cli import main


def _parse(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["fusion_report", *argv])
    builder = ArgsBuilder()
    builder.build()
    return builder.parse()


@pytest.mark.parametrize("flag", ["-no_ssl", "--no-ssl"])
def test_no_ssl_flag_and_alias(monkeypatch, flag):
    assert _parse(monkeypatch, "download", flag, "db").no_ssl is True


def test_ssl_verification_is_default(monkeypatch):
    params = _parse(monkeypatch, "download", "db")
    assert params.no_ssl is False
    assert params.allow_missing is False
    assert params.mitelman_file is None and params.fusiongdb2_url is None
    assert params.cosmic_version == "v101"


def test_cosmic_version_flag(monkeypatch):
    assert (
        _parse(monkeypatch, "download", "--cosmic-version", "v103", "db").cosmic_version == "v103"
    )


def test_download_source_override_flags(monkeypatch):
    params = _parse(
        monkeypatch,
        "download",
        "--allow-missing",
        "--mitelman-file",
        "m.zip",
        "--fusiongdb2-url",
        "https://mirror.example.org/f.txt",
        "--cosmic-file",
        "c.tsv.gz",
        "db",
    )
    assert params.allow_missing is True
    assert params.mitelman_file == "m.zip"
    assert params.fusiongdb2_url == "https://mirror.example.org/f.txt"
    assert params.cosmic_file == "c.tsv.gz"


def test_main_prints_readable_error_and_exits_1(monkeypatch, tmp_path, caplog):
    missing = tmp_path / "missing.zip"
    monkeypatch.setattr(
        sys, "argv", ["fusion_report", "createdb", str(tmp_path / "db"), "--mitelman", str(missing)]
    )
    assert main() == 1
    assert "Mitelman file not found" in caplog.text
    assert "--debug" in caplog.text
    assert "Traceback" not in caplog.text


def test_main_debug_shows_traceback(monkeypatch, tmp_path, caplog):
    missing = tmp_path / "missing.zip"
    monkeypatch.setattr(
        sys,
        "argv",
        ["fusion_report", "--debug", "createdb", str(tmp_path / "db"), "--mitelman", str(missing)],
    )
    assert main() == 1
    assert "Traceback" in caplog.text


def test_main_success_returns_0(monkeypatch, tmp_path):
    fixture = str(Path(__file__).parent / "test_data" / "fusiongdb2_mini.txt")
    monkeypatch.setattr(
        sys, "argv", ["fusion_report", "createdb", str(tmp_path / "db"), "--fusiongdb2", fixture]
    )
    assert main() == 0
