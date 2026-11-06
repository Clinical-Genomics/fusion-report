"""Tests for `fusion_report check-sources` and offline PR CI."""

import json
from argparse import Namespace
from pathlib import Path

import pytest

from fusion_report.check_sources import CheckSources, check_url
from fusion_report.common.exceptions.download import DownloadException
from fusion_report.common.fetch import check_head, make_session
from fusion_report.settings import Settings

TEST_DATA = Path(__file__).parent / "test_data"
ZIP = (200, {"Content-Type": "application/zip"}, (TEST_DATA / "mitelman_mini.zip").read_bytes())
TXT = (200, {"Content-Type": "text/plain"}, (TEST_DATA / "fusiongdb2_mini.txt").read_bytes())
HTML = (429, {"Content-Type": "text/html"}, b"<!DOCTYPE html><html>blocked</html>")
COSMIC_UP = (400, {"Content-Type": "application/json"}, b'{"name":"BadRequestError"}')
REPO = Path(__file__).parent.parent


@pytest.fixture
def server(http_server, monkeypatch):
    """All sources healthy by default."""
    monkeypatch.setitem(Settings.MITELMAN, "HOSTNAME", http_server.url("/mitelman"))
    monkeypatch.setitem(Settings.FUSIONGDB2, "HOSTNAME", http_server.url("/fusiongdb2"))
    monkeypatch.setitem(Settings.COSMIC, "HOSTNAME", http_server.url("/cosmic"))
    http_server.add(f"/mitelman/{Settings.MITELMAN['FILE']}", ZIP)
    http_server.add(f"/fusiongdb2/{Settings.FUSIONGDB2['FILE']}", TXT)
    http_server.add("/cosmic", COSMIC_UP)
    return http_server


def _params(tmp_path=None, strict=False):
    return Namespace(
        no_ssl=False, strict=strict, json=str(tmp_path / "r.json") if tmp_path else None
    )


@pytest.mark.parametrize(
    "head, fmt, content_type, error",
    [
        (b"PK\x03\x04rest", "zip", "application/zip", None),
        (b"\x1f\x8brest", "gzip", "", None),
        (b"a\tb\n", "text", "text/plain", None),
        (b"a\tb\n", "text", "text/html", "HTML page"),
        (b" <html>", "zip", "", "HTML page"),
        (b"nope", "zip", "", "not a valid zip"),
        (b"x" * 600, "tar", "", "not a valid tar"),
        (b"", "text", "", "empty"),
    ],
)
def test_check_head(head, fmt, content_type, error):
    result = check_head(head, fmt, content_type)
    assert result is None if error is None else error in result


def test_check_url_ok_and_broken(server):
    session = make_session()
    ok = check_url(session, server.url(f"/mitelman/{Settings.MITELMAN['FILE']}"), "zip")
    assert ok["ok"] and ok["status"] == 200
    server.add("/blocked", HTML)
    blocked = check_url(session, server.url("/blocked"), "text")
    assert not blocked["ok"] and "HTTP 429" in blocked["error"]
    server.add("/wrong", (200, {"Content-Type": "application/zip"}, b"not a zip"))
    assert "not a valid zip" in check_url(session, server.url("/wrong"), "zip")["error"]


def test_all_sources_ok_writes_json(server, tmp_path):
    CheckSources(_params(tmp_path))
    results = json.loads((tmp_path / "r.json").read_text())
    assert all(result["ok"] for result in results.values())
    assert results["cosmic"]["urls"][0]["status"] == 400


def test_broken_optional_source_only_warns(server, tmp_path, caplog):
    server.add(f"/fusiongdb2/{Settings.FUSIONGDB2['FILE']}", HTML)
    CheckSources(_params(tmp_path))
    assert "Broken optional source(s): FusionGDB2" in caplog.text
    assert json.loads((tmp_path / "r.json").read_text())["fusiongdb2"]["ok"] is False


def test_broken_optional_source_fails_with_strict(server):
    server.add(f"/fusiongdb2/{Settings.FUSIONGDB2['FILE']}", HTML)
    with pytest.raises(DownloadException, match="FusionGDB2"):
        CheckSources(_params(strict=True))


def test_broken_required_source_fails(server):
    server.add(f"/mitelman/{Settings.MITELMAN['FILE']}", HTML)
    with pytest.raises(DownloadException, match="Broken database source.*Mitelman"):
        CheckSources(_params())


def test_cosmic_api_html_is_broken(server):
    server.add("/cosmic", (503, {"Content-Type": "text/html"}, b"<html>down</html>"))
    with pytest.raises(DownloadException, match="COSMIC"):
        CheckSources(_params())


def test_source_ok_if_any_mirror_works(server, monkeypatch):
    server.add(f"/fusiongdb2/{Settings.FUSIONGDB2['FILE']}", HTML)
    monkeypatch.setitem(Settings.MIRRORS, "fusiongdb2", [server.add("/mirror.txt", TXT)])
    CheckSources(_params(strict=True))


def test_pr_integration_tests_do_not_download_remote_databases():
    """PR CI must not depend on upstream sources; they are checked by check_sources.yml."""
    workflow = (REPO / ".github" / "workflows" / "integration_tests.yml").read_text()
    for host in ("compbio.uth.edu", "storage.googleapis.com", "wget "):
        assert host not in workflow
