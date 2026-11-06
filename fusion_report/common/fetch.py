"""Validated HTTP downloads for remote database sources.

Every remote file goes through `download_file`, which:

* uses a shared `requests.Session` with retries (incl. 429/5xx), a timeout and an identifying
  User-Agent,
* fails on non-2xx responses instead of saving the error page,
* rejects HTML pages served in place of a data file (moved/blocked sources),
* checks the file's magic bytes and the received size against Content-Length,
* writes to `<file>.part` and only moves it into place once all checks passed.
"""

import os
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from fusion_report.common.exceptions.download import DownloadException
from fusion_report.common.logger import Logger
from fusion_report.settings import Settings

LOG = Logger(__name__)

USER_AGENT = (
    f"fusion-report/{Settings.VERSION} (+https://github.com/Clinical-Genomics/fusion-report)"
)
RETRY_STATUSES = (429, 500, 502, 503, 504)
RETRY_TOTAL = 5
RETRY_BACKOFF = 2.0
TIMEOUT = (10, 300)  # (connect, read) seconds
CHUNK_SIZE = 1024 * 1024

# Expected leading bytes per file format. "text" files must simply not look like HTML.
MAGIC = {
    "zip": (b"PK\x03\x04",),
    "gzip": (b"\x1f\x8b",),
}
TAR_MAGIC_OFFSET = 257
TAR_MAGIC = b"ustar"
HTML_PREFIXES = (b"<!doctype", b"<html", b"<?xml", b"<head", b"<body")


class FetchError(DownloadException):
    """Raised when a remote file could not be downloaded or is not the expected file."""


def make_session(no_ssl: bool = False) -> requests.Session:
    """Create a session with retries, an identifying User-Agent and SSL verification."""
    retry = Retry(
        total=RETRY_TOTAL,
        backoff_factor=RETRY_BACKOFF,
        status_forcelist=RETRY_STATUSES,
        allowed_methods=frozenset(["GET", "HEAD"]),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers["User-Agent"] = USER_AGENT
    session.verify = not no_ssl
    return session


def looks_like_html(head: bytes) -> bool:
    """Return True if the first bytes of a file look like an HTML/XML page."""
    return head.lstrip().lower().startswith(HTML_PREFIXES)


def check_magic(path: str, fmt: str, source: str = "") -> None:
    """Verify that the file at `path` matches the expected format.

    Args:
        fmt: one of "zip", "gzip", "tar", "text" or "binary" (no check)

    Raises:
        FetchError
    """
    with open(path, "rb") as handle:
        head = handle.read(512)

    prefix = f"{source}: " if source else ""
    if not head:
        raise FetchError(f"{prefix}downloaded file is empty")
    if fmt != "binary" and looks_like_html(head):
        raise FetchError(
            f"{prefix}expected a {fmt} file but received an HTML page. The upstream source may "
            "have moved or be blocking automated downloads."
        )
    if fmt in MAGIC and not head.startswith(MAGIC[fmt]):
        raise FetchError(f"{prefix}downloaded file is not a valid {fmt} file")
    if fmt == "tar" and head[TAR_MAGIC_OFFSET : TAR_MAGIC_OFFSET + len(TAR_MAGIC)] != TAR_MAGIC:
        raise FetchError(f"{prefix}downloaded file is not a valid tar archive")


def download_file(
    url: str,
    dest: str,
    fmt: str = "binary",
    no_ssl: bool = False,
    session: Optional[requests.Session] = None,
    source: str = "",
) -> str:
    """Download `url` to `dest` and validate it.

    Returns:
        the destination path

    Raises:
        FetchError: on HTTP errors, HTML instead of data, wrong format or truncated downloads
    """
    LOG.info(f"Downloading {url}")
    own_session = session is None
    session = session or make_session(no_ssl)
    prefix = f"{source}: " if source else ""
    part = f"{dest}.part"
    try:
        with session.get(url, stream=True, timeout=TIMEOUT) as response:
            if not response.ok:
                raise FetchError(
                    f"{prefix}HTTP {response.status_code} {response.reason} for {response.url} "
                    f"(content type: {response.headers.get('Content-Type', 'unknown')})"
                )
            content_type = response.headers.get("Content-Type", "")
            if fmt != "binary" and "text/html" in content_type.lower():
                raise FetchError(
                    f"{prefix}expected a {fmt} file but received an HTML page ({content_type}) "
                    f"from {response.url}. The upstream source may have moved or be blocking "
                    "automated downloads."
                )
            received = 0
            with open(part, "wb") as out_file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        out_file.write(chunk)
                        received += len(chunk)
            expected = response.headers.get("Content-Length")
            encoded = response.headers.get("Content-Encoding")
            if expected is not None and not encoded and int(expected) != received:
                raise FetchError(
                    f"{prefix}truncated download from {url}: received {received} of "
                    f"{expected} bytes"
                )
        check_magic(part, fmt, source)
        os.replace(part, dest)
        return dest
    except requests.exceptions.SSLError as ex:
        raise FetchError(
            f"{prefix}SSL certificate verification failed for {url}. If you are behind a proxy "
            "that intercepts TLS, set REQUESTS_CA_BUNDLE or re-run with --no-ssl. "
            f"(details: {ex})"
        ) from ex
    except requests.exceptions.RequestException as ex:
        raise FetchError(f"{prefix}could not download {url}: {ex}") from ex
    finally:
        if os.path.exists(part):
            os.remove(part)
        if own_session:
            session.close()
