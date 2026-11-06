"""Unit tests for the source registry and mirror/checksum handling."""

import base64
import hashlib

import pytest

from fusion_report.common.fetch import FetchError, download_file, download_source
from fusion_report.data.sources import Source, get_source, get_sources
from fusion_report.settings import Settings

BODY = b"id1\tA-B\tA\t1\tB\t2\n"
OK = (200, {"Content-Type": "text/plain"}, BODY)
GONE = (404, {"Content-Type": "text/html"}, b"<html>gone</html>")


def _source(urls, sha256=None):
    return Source(
        key="test",
        name="TestDB",
        required=False,
        weight=0.0,
        version="1",
        filename="file.txt",
        fmt="text",
        urls=urls,
        sha256=sha256,
    )


def test_registry_describes_all_sources():
    sources = get_sources()
    assert set(sources) == {"cosmic", "mitelman", "fusiongdb2"}
    assert sources["cosmic"].required and sources["mitelman"].required
    assert not sources["fusiongdb2"].required
    assert sources["fusiongdb2"].weight == 0.0
    assert sources["mitelman"].weight == Settings.FUSION_WEIGHTS["mitelman"]
    assert sources["fusiongdb2"].sha256 == Settings.FUSIONGDB2["SHA256"]
    assert sources["mitelman"].urls[0].endswith("/mitelman_db.zip")


def test_registry_appends_mirrors_after_primary(monkeypatch):
    monkeypatch.setitem(Settings.MIRRORS, "fusiongdb2", ["https://mirror.example.org/f.txt"])
    urls = get_source("fusiongdb2").urls
    assert urls[0].startswith(Settings.FUSIONGDB2["HOSTNAME"])
    assert urls[1] == "https://mirror.example.org/f.txt"


def test_download_source_falls_back_to_next_url(http_server, tmp_path):
    first = http_server.add("/primary", GONE)
    second = http_server.add("/mirror", OK)
    used = download_source(_source([first, second]), str(tmp_path / "file.txt"))
    assert used == second
    assert (tmp_path / "file.txt").read_bytes() == BODY


def test_download_source_lists_every_failed_url(http_server, tmp_path):
    first = http_server.add("/primary", GONE)
    second = http_server.add("/mirror", (200, {"Content-Type": "text/html"}, b"<html>"))
    with pytest.raises(FetchError) as excinfo:
        download_source(_source([first, second]), str(tmp_path / "file.txt"))
    message = str(excinfo.value)
    assert "all 2 download URLs failed" in message
    assert "HTTP 404" in message and "HTML page" in message


def test_download_source_without_urls(tmp_path):
    with pytest.raises(FetchError, match="no download URL configured"):
        download_source(_source([]), str(tmp_path / "file.txt"))


def test_sha256_match(http_server, tmp_path):
    url = http_server.add("/file", OK)
    download_source(_source([url], hashlib.sha256(BODY).hexdigest()), str(tmp_path / "f"))


def test_sha256_mismatch_rejects_file(http_server, tmp_path):
    url = http_server.add("/file", OK)
    with pytest.raises(FetchError, match="sha256 checksum mismatch"):
        download_source(_source([url], "0" * 64), str(tmp_path / "f"))
    assert not (tmp_path / "f").exists()


def test_goog_md5_is_verified(http_server, tmp_path):
    good = base64.b64encode(hashlib.md5(BODY).digest()).decode()
    url = http_server.add("/ok", (200, {"x-goog-hash": f"crc32c=AAAA==, md5={good}"}, BODY))
    download_file(url, str(tmp_path / "ok"), fmt="text")

    bad = base64.b64encode(b"0" * 16).decode()
    url = http_server.add("/bad", (200, {"x-goog-hash": f"md5={bad}"}, BODY))
    with pytest.raises(FetchError, match="md5 checksum mismatch"):
        download_file(url, str(tmp_path / "bad"), fmt="text")
