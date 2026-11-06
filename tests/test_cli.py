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
    assert _parse(monkeypatch, "download", "db").no_ssl is False


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
