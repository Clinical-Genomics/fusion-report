"""Validated HTTP downloads for remote database sources.

Every remote file goes through `download_file`, which:

* uses a shared `requests.Session` with retries (incl. 429/5xx), a timeout and an identifying
  User-Agent,
* fails on non-2xx responses instead of saving the error page,
* rejects HTML pages served in place of a data file (moved/blocked sources),
* checks the file's magic bytes and the received size against Content-Length,
* verifies a pinned sha256 and, when the server provides one (Google Cloud Storage), the md5,
* writes to `<file>.part` and only moves it into place once all checks passed.
"""

import base64
import hashlib
import os
from typing import Dict, List, Optional

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
    sha256: Optional[str] = None,
) -> str:
    """Download `url` to `dest` and validate it.

    Returns:
        the destination path

    Raises:
        FetchError: on HTTP errors, HTML instead of data, wrong format, truncated downloads or
            checksum mismatches
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
            sha = hashlib.sha256()
            md5 = hashlib.md5()  # nosec: only used to compare with the server-provided md5
            with open(part, "wb") as out_file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        out_file.write(chunk)
                        sha.update(chunk)
                        md5.update(chunk)
                        received += len(chunk)
            expected = response.headers.get("Content-Length")
            encoded = response.headers.get("Content-Encoding")
            if expected is not None and not encoded and int(expected) != received:
                raise FetchError(
                    f"{prefix}truncated download from {url}: received {received} of "
                    f"{expected} bytes"
                )
            server_md5 = _goog_md5(response.headers)
            if server_md5 and not encoded and server_md5 != md5.digest():
                raise FetchError(f"{prefix}md5 checksum mismatch for {url}")
        check_magic(part, fmt, source)
        if sha256 and sha.hexdigest() != sha256.lower():
            raise FetchError(
                f"{prefix}sha256 checksum mismatch for {url}: expected {sha256}, "
                f"got {sha.hexdigest()}. The file differs from the known version."
            )
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


def _goog_md5(headers) -> Optional[bytes]:
    """Return the md5 digest from a Google Cloud Storage `x-goog-hash` header, if present."""
    for part in headers.get("x-goog-hash", "").split(","):
        name, _, value = part.strip().partition("=")
        if name == "md5" and value:
            try:
                return base64.b64decode(value)
            except ValueError:
                return None
    return None


def download_source(source, dest: str, no_ssl: bool = False, urls: Optional[List[str]] = None):
    """Download a registry `Source`, trying its URLs (or `urls`) in order.

    Returns:
        the URL the file was downloaded from

    Raises:
        FetchError: listing every attempted URL if all of them fail
    """
    candidates = urls if urls is not None else source.urls
    if not candidates:
        raise FetchError(f"{source.name}: no download URL configured")
    errors: Dict[str, str] = {}
    with make_session(no_ssl) as session:
        for url in candidates:
            try:
                download_file(
                    url,
                    dest,
                    fmt=source.fmt,
                    session=session,
                    source=source.name,
                    sha256=source.sha256,
                )
                return url
            except FetchError as ex:
                errors[url] = str(ex)
                if url != candidates[-1]:
                    LOG.warning(f"{ex} Trying the next mirror.")
    if len(errors) == 1:
        raise FetchError(next(iter(errors.values())))
    attempts = "\n".join(f"  - {err}" for err in errors.values())
    raise FetchError(f"{source.name}: all {len(errors)} download URLs failed:\n{attempts}")
