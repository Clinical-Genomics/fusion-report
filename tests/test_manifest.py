"""Tests for db_manifest.json: --allow-missing, local files, URL overrides and provenance."""

import hashlib
import json
import sys
from argparse import Namespace
from pathlib import Path
from unittest import mock

import pytest

from fusion_report.common.exceptions.download import DownloadException
from fusion_report.common.manifest import (
    MANIFEST_FILE,
    Manifest,
    file_sha256,
    read_manifest,
    redact,
)
from fusion_report.createdb import CreateDB
from fusion_report.data.sources import get_source
from fusion_report.download import Download
from fusion_report.settings import Settings

TEST_DATA = Path(__file__).parent / "test_data"
MITELMAN_ZIP = TEST_DATA / "mitelman_mini.zip"
FUSIONGDB2_TXT = TEST_DATA / "fusiongdb2_mini.txt"
HTML = (404, {"Content-Type": "text/html"}, b"<html>gone</html>")


def _params(output, **overrides):
    values = dict(
        output=str(output),
        no_mitelman=False,
        no_fusiongdb2=False,
        no_cosmic=True,
        no_ssl=False,
        qiagen=False,
        allow_missing=False,
    )
    values.update(overrides)
    return Namespace(**values)


def _manifest(path):
    return json.loads((Path(path) / MANIFEST_FILE).read_text())


@pytest.fixture
def server(http_server, monkeypatch):
    """Mitelman and FusionGDB2 point at the local server and are unavailable by default."""
    monkeypatch.setitem(Settings.MITELMAN, "HOSTNAME", http_server.url("/mitelman"))
    monkeypatch.setitem(Settings.FUSIONGDB2, "HOSTNAME", http_server.url("/fusiongdb2"))
    monkeypatch.setitem(Settings.FUSIONGDB2, "SHA256", None)
    http_server.add(f"/mitelman/{Settings.MITELMAN['FILE']}", HTML)
    http_server.add(f"/fusiongdb2/{Settings.FUSIONGDB2['FILE']}", HTML)
    return http_server


# --- manifest helpers ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "argv, expected",
    [
        (
            ["--cosmic_usr", "me", "--cosmic_passwd", "pw"],
            ["--cosmic_usr", "***", "--cosmic_passwd", "***"],
        ),
        (["--cosmic_token=abc", "db"], ["--cosmic_token=***", "db"]),
        (["download", "--no-cosmic", "db"], ["download", "--no-cosmic", "db"]),
    ],
)
def test_redact(argv, expected):
    assert redact(argv) == expected


def test_manifest_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["fusion_report", "download", "--cosmic_passwd", "pw", "db"])
    manifest = Manifest("download")
    manifest.record_file(get_source("mitelman"), str(MITELMAN_ZIP), "https://x/y.zip", rows=5)
    manifest.write(str(tmp_path))

    data = read_manifest(str(tmp_path))
    assert data["fusion_report_version"] == Settings.VERSION
    assert data["argv"] == ["download", "--cosmic_passwd", "***", "db"]
    entry = data["sources"]["mitelman"]
    assert entry["status"] == "ok" and entry["db_file"] == "mitelman.db"
    assert entry["sha256"] == hashlib.sha256(MITELMAN_ZIP.read_bytes()).hexdigest()
    assert entry["bytes"] == MITELMAN_ZIP.stat().st_size and entry["rows"] == 5


def test_read_manifest_missing_or_invalid(tmp_path, caplog):
    assert read_manifest(str(tmp_path)) is None
    (tmp_path / MANIFEST_FILE).write_text("{broken")
    assert read_manifest(str(tmp_path)) is None
    assert "Could not read" in caplog.text


def test_file_sha256(tmp_path):
    path = tmp_path / "f"
    path.write_bytes(b"abc")
    assert file_sha256(str(path)) == hashlib.sha256(b"abc").hexdigest()


# --- download -----------------------------------------------------------------------------


def test_download_writes_manifest_on_failure(server, tmp_path):
    with pytest.raises(DownloadException, match="Mitelman"):
        Download(_params(tmp_path))
    sources = _manifest(tmp_path)["sources"]
    assert sources["mitelman"]["status"] == "failed" and sources["mitelman"]["required"]
    assert sources["fusiongdb2"]["status"] == "skipped"
    assert sources["cosmic"]["status"] == "disabled"
    assert "HTTP 404" in sources["mitelman"]["error"]


def test_allow_missing_turns_required_failures_into_warnings(server, tmp_path, caplog):
    server.add(f"/fusiongdb2/{Settings.FUSIONGDB2['FILE']}", (200, {}, FUSIONGDB2_TXT.read_bytes()))
    Download(_params(tmp_path, allow_missing=True))
    assert (tmp_path / "fusiongdb2.db").exists()
    assert _manifest(tmp_path)["sources"]["mitelman"]["status"] == "skipped"
    assert "Mitelman is optional and was skipped" in caplog.text


def test_allow_missing_still_fails_when_nothing_was_built(server, tmp_path):
    with pytest.raises(DownloadException, match="No database could be downloaded"):
        Download(_params(tmp_path, allow_missing=True))


def test_local_files_skip_the_network(server, tmp_path):
    Download(
        _params(tmp_path, mitelman_file=str(MITELMAN_ZIP), fusiongdb2_file=str(FUSIONGDB2_TXT))
    )
    assert server.hits == {}
    sources = _manifest(tmp_path)["sources"]
    assert sources["mitelman"]["origin"] == f"file:{MITELMAN_ZIP}"
    assert sources["fusiongdb2"]["rows"] == 6
    assert (tmp_path / "mitelman.db").exists() and (tmp_path / "fusiongdb2.db").exists()


def test_relative_local_file_is_resolved_before_chdir(server, tmp_path, monkeypatch):
    monkeypatch.chdir(TEST_DATA)
    Download(_params(tmp_path / "db", mitelman_file="mitelman_mini.zip", no_fusiongdb2=True))
    assert (tmp_path / "db" / "mitelman.db").exists()


def test_missing_local_file(server, tmp_path):
    with pytest.raises(DownloadException, match="Mitelman: local file not found"):
        Download(_params(tmp_path, mitelman_file=str(tmp_path / "nope.zip"), no_fusiongdb2=True))


def test_url_override_is_used_and_recorded_without_query(server, tmp_path):
    url = server.add("/elsewhere/m.zip", (200, {}, MITELMAN_ZIP.read_bytes()))
    Download(_params(tmp_path, mitelman_url=f"{url}?token=secret", no_fusiongdb2=True))
    assert server.hits["/elsewhere/m.zip"] == 1
    assert f"/mitelman/{Settings.MITELMAN['FILE']}" not in server.hits
    assert _manifest(tmp_path)["sources"]["mitelman"]["origin"] == url


def test_cosmic_file_needs_no_credentials(server, tmp_path):
    from fusion_report.common.db_builders import cosmic_columns

    columns = cosmic_columns()
    row = {name: "" for name in columns}
    row.update(COSMIC_SAMPLE_ID="1", FIVE_PRIME_GENE_SYMBOL="BCR", THREE_PRIME_GENE_SYMBOL="ABL1")
    cosmic = tmp_path / "cosmic.tsv"
    cosmic.write_text("\t".join(columns) + "\n" + "\t".join(row[c] for c in columns) + "\n")
    with mock.patch("fusion_report.download.Net.get_cosmic_token") as token:
        Download(
            _params(
                tmp_path / "db",
                no_cosmic=False,
                cosmic_file=str(cosmic),
                no_mitelman=True,
                no_fusiongdb2=True,
            )
        )
    token.assert_not_called()
    assert _manifest(tmp_path / "db")["sources"]["cosmic"]["rows"] == 1


# --- createdb and run -----------------------------------------------------------------------


def test_createdb_writes_manifest(tmp_path):
    CreateDB(
        Namespace(output=str(tmp_path), cosmic=None, mitelman=str(MITELMAN_ZIP), fusiongdb2=None)
    )
    sources = _manifest(tmp_path)["sources"]
    assert _manifest(tmp_path)["command"] == "createdb"
    assert (
        sources["mitelman"]["origin"] == f"file:{MITELMAN_ZIP}" and sources["mitelman"]["rows"] == 5
    )
    assert "fusiongdb2" not in sources


def test_run_skips_fusiongdb2_recorded_as_skipped(tmp_path, caplog):
    from fusion_report.app import App

    CreateDB(
        Namespace(output=str(tmp_path), cosmic=None, mitelman=str(MITELMAN_ZIP), fusiongdb2=None)
    )
    manifest = _manifest(tmp_path)
    manifest["sources"]["fusiongdb2"] = {"name": "FusionGDB2", "status": "skipped"}
    (tmp_path / MANIFEST_FILE).write_text(json.dumps(manifest))

    app = App()
    params = Namespace(
        db_path=str(tmp_path), no_cosmic=True, no_mitelman=False, no_fusiongdb2=False
    )
    app.enrich(params)

    assert "FusionGDB2 was not built for this database folder" in caplog.text
    assert "Optional database file" not in caplog.text
    assert "Database Mitelman: version latest, 5 rows" in caplog.text
    assert not (tmp_path / "fusiongdb2.db").exists()
