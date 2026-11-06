"""Unit tests for validated downloads (fusion_report.common.fetch)."""

import gzip
import io
import tarfile
import zipfile

import pytest

from fusion_report.common.fetch import USER_AGENT, FetchError, check_magic, download_file

HTML_429 = (429, {"Content-Type": "text/html"}, b"<!DOCTYPE html><html>Too Many Requests</html>")
TSV = b"id1\tA-B\tA\t1\tB\t2\n"


def _zip_bytes() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("MBCA.TXT.DATA", "data")
    return buffer.getvalue()


def _tar_bytes() -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        info = tarfile.TarInfo("file.txt")
        info.size = 4
        archive.addfile(info, io.BytesIO(b"data"))
    return buffer.getvalue()


@pytest.mark.parametrize(
    "fmt, body",
    [
        ("zip", _zip_bytes()),
        ("gzip", gzip.compress(b"data")),
        ("tar", _tar_bytes()),
        ("text", TSV),
    ],
)
def test_download_valid_file(http_server, tmp_path, fmt, body):
    url = http_server.add("/file", (200, {"Content-Type": "application/octet-stream"}, body))
    dest = tmp_path / "file"
    download_file(url, str(dest), fmt=fmt)
    assert dest.read_bytes() == body
    assert not (tmp_path / "file.part").exists()


def test_download_retries_429_then_succeeds(http_server, tmp_path):
    url = http_server.add("/file", HTML_429, (200, {"Content-Type": "text/plain"}, TSV))
    download_file(url, str(tmp_path / "file"), fmt="text")
    assert http_server.hits["/file"] == 2


def test_download_persistent_500_fails_with_status(http_server, tmp_path):
    url = http_server.add("/file", (500, {"Content-Type": "text/plain"}, b"boom"))
    with pytest.raises(FetchError, match="Mitelman:.*(500|too many 500)"):
        download_file(url, str(tmp_path / "file"), fmt="zip", source="Mitelman")
    assert not (tmp_path / "file").exists()


def test_download_404_fails_and_writes_nothing(http_server, tmp_path):
    url = http_server.add("/file", (404, {"Content-Type": "text/html"}, b"<html>gone</html>"))
    with pytest.raises(FetchError, match="HTTP 404"):
        download_file(url, str(tmp_path / "file"), fmt="text")
    assert list(tmp_path.iterdir()) == []


def test_download_rejects_html_content_type(http_server, tmp_path):
    url = http_server.add("/file", (200, {"Content-Type": "text/html; charset=utf-8"}, b"<html>"))
    with pytest.raises(FetchError, match="FusionGDB2: expected a text file but received an HTML"):
        download_file(url, str(tmp_path / "file"), fmt="text", source="FusionGDB2")
    assert list(tmp_path.iterdir()) == []


def test_download_rejects_html_body_with_wrong_content_type(http_server, tmp_path):
    url = http_server.add("/file", (200, {"Content-Type": "text/plain"}, b"  <!DOCTYPE html>"))
    with pytest.raises(FetchError, match="received an HTML page"):
        download_file(url, str(tmp_path / "file"), fmt="text")


def test_download_rejects_wrong_magic_bytes(http_server, tmp_path):
    url = http_server.add("/file", (200, {"Content-Type": "application/zip"}, b"not a zip"))
    with pytest.raises(FetchError, match="not a valid zip file"):
        download_file(url, str(tmp_path / "file"), fmt="zip")
    assert list(tmp_path.iterdir()) == []


def test_download_rejects_truncated_file(http_server, tmp_path):
    body = _zip_bytes()
    url = http_server.add(
        "/file", (200, {"Content-Type": "application/zip", "Content-Length": "999999"}, body)
    )
    with pytest.raises(FetchError):
        download_file(url, str(tmp_path / "file"), fmt="zip")
    assert list(tmp_path.iterdir()) == []


def test_download_sends_identifying_user_agent(http_server, tmp_path):
    url = http_server.add("/file", (200, {}, TSV))
    download_file(url, str(tmp_path / "file"), fmt="text")
    assert http_server.request_headers[-1]["User-Agent"] == USER_AGENT


def test_connection_error_is_fetch_error(tmp_path):
    with pytest.raises(FetchError, match="could not download"):
        download_file("http://127.0.0.1:9/file", str(tmp_path / "file"), fmt="text")


def test_check_magic_rejects_empty_file(tmp_path):
    empty = tmp_path / "empty"
    empty.write_bytes(b"")
    with pytest.raises(FetchError, match="empty"):
        check_magic(str(empty), "text")
