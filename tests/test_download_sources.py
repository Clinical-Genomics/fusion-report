"""End-to-end tests of `download` against a local HTTP server: validation, per-source
isolation and FusionGDB2 being optional."""

from argparse import Namespace
from pathlib import Path

import pytest

from fusion_report.common.exceptions.download import DownloadException
from fusion_report.download import Download
from fusion_report.settings import Settings

TEST_DATA = Path(__file__).parent / "test_data"
MITELMAN_ZIP = (TEST_DATA / "mitelman_mini.zip").read_bytes()
FUSIONGDB2_TXT = (TEST_DATA / "fusiongdb2_mini.txt").read_bytes()
HTML_429 = (429, {"Content-Type": "text/html"}, b"<!DOCTYPE html><html>Just a moment...</html>")


def _params(output, **overrides):
    values = dict(
        output=str(output),
        no_mitelman=False,
        no_fusiongdb2=False,
        no_cosmic=True,
        no_ssl=False,
        qiagen=False,
    )
    values.update(overrides)
    return Namespace(**values)


@pytest.fixture
def sources(http_server, monkeypatch):
    """Point Mitelman and FusionGDB2 at the local server; serve valid files by default."""
    monkeypatch.setitem(Settings.MITELMAN, "HOSTNAME", http_server.url("/mitelman"))
    monkeypatch.setitem(Settings.FUSIONGDB2, "HOSTNAME", http_server.url("/fusiongdb2"))
    # the fixture is not the real (pinned) FusionGDB2 file
    monkeypatch.setitem(Settings.FUSIONGDB2, "SHA256", None)
    mitelman_path = f"/mitelman/{Settings.MITELMAN['FILE']}"
    fusiongdb2_path = f"/fusiongdb2/{Settings.FUSIONGDB2['FILE']}"
    http_server.add(mitelman_path, (200, {"Content-Type": "application/zip"}, MITELMAN_ZIP))
    http_server.add(fusiongdb2_path, (200, {"Content-Type": "text/plain"}, FUSIONGDB2_TXT))
    return http_server, mitelman_path, fusiongdb2_path


def test_download_all_sources(sources, tmp_path):
    Download(_params(tmp_path))
    assert (tmp_path / "mitelman.db").exists()
    assert (tmp_path / "fusiongdb2.db").exists()
    assert (tmp_path / "DB-timestamp.txt").exists()
    assert not (tmp_path / "tmp_dir").exists()


def test_fusiongdb2_html_is_only_a_warning(sources, tmp_path, caplog):
    server, _, fusiongdb2_path = sources
    server.add(fusiongdb2_path, HTML_429)

    Download(_params(tmp_path))

    assert (tmp_path / "mitelman.db").exists()
    assert not (tmp_path / "fusiongdb2.db").exists()
    assert not (tmp_path / "tmp_dir").exists()
    assert "FusionGDB2" in caplog.text and "optional" in caplog.text


def test_fusiongdb2_unexpected_columns_is_only_a_warning(sources, tmp_path, caplog):
    server, _, fusiongdb2_path = sources
    server.add(fusiongdb2_path, (200, {"Content-Type": "text/plain"}, b"a\tb\nc\td\n"))

    Download(_params(tmp_path))

    assert (tmp_path / "mitelman.db").exists()
    assert not (tmp_path / "fusiongdb2.db").exists()
    assert "unexpected file format" in caplog.text


def test_required_mitelman_failure_raises_but_keeps_other_dbs(sources, tmp_path):
    server, mitelman_path, _ = sources
    server.add(mitelman_path, HTML_429)

    with pytest.raises(DownloadException, match="Mitelman: HTTP 429"):
        Download(_params(tmp_path))

    # FusionGDB2 is still downloaded and kept, and the temporary directory is removed
    assert (tmp_path / "fusiongdb2.db").exists()
    assert not (tmp_path / "mitelman.db").exists()
    assert not (tmp_path / "tmp_dir").exists()


def test_mitelman_zip_without_data_file_raises(sources, tmp_path):
    import io
    import zipfile

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("README.txt", "nothing here")
    server, mitelman_path, _ = sources
    server.add(mitelman_path, (200, {"Content-Type": "application/zip"}, buffer.getvalue()))

    with pytest.raises(DownloadException, match="MBCA.TXT.DATA not found"):
        Download(_params(tmp_path, no_fusiongdb2=True))


def test_no_fusiongdb2_does_not_request_it(sources, tmp_path):
    server, _, fusiongdb2_path = sources
    Download(_params(tmp_path, no_fusiongdb2=True))
    assert fusiongdb2_path not in server.hits


def test_fusiongdb2_checksum_mismatch_is_only_a_warning(sources, tmp_path, caplog, monkeypatch):
    monkeypatch.setitem(Settings.FUSIONGDB2, "SHA256", "0" * 64)
    Download(_params(tmp_path))
    assert (tmp_path / "mitelman.db").exists()
    assert not (tmp_path / "fusiongdb2.db").exists()
    assert "sha256 checksum mismatch" in caplog.text


def test_fusiongdb2_falls_back_to_mirror(sources, tmp_path, monkeypatch):
    server, _, fusiongdb2_path = sources
    server.add(fusiongdb2_path, HTML_429)
    mirror = server.add("/mirror/fgdb2.txt", (200, {"Content-Type": "text/plain"}, FUSIONGDB2_TXT))
    monkeypatch.setitem(Settings.MIRRORS, "fusiongdb2", [mirror])

    Download(_params(tmp_path))

    assert (tmp_path / "fusiongdb2.db").exists()
    assert server.hits["/mirror/fgdb2.txt"] == 1
