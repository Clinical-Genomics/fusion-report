"""Check that the remote database sources are reachable and serve the expected files.

Used by the scheduled `check_sources` workflow to notice upstream changes (moved files, blocked
downloads, HTML instead of data) before users do. Only the first bytes of each file are
fetched. Exits with an error if a required source is broken, or any source with --strict.
"""

import json
from argparse import Namespace
from typing import Any, Dict, List

import requests

from fusion_report.common.exceptions.download import DownloadException
from fusion_report.common.fetch import TIMEOUT, check_head, make_session
from fusion_report.common.logger import Logger
from fusion_report.data.sources import Source, get_sources
from fusion_report.settings import Settings

LOG = Logger(__name__)
HEAD_BYTES = 1024
# Unauthenticated requests to the COSMIC scripted-download API are answered with a JSON error.
COSMIC_API_UP_STATUSES = (200, 400, 401)


def check_url(session: requests.Session, url: str, fmt: str) -> Dict[str, Any]:
    """Fetch the first bytes of `url` and check status, content type and magic bytes."""
    result: Dict[str, Any] = {"url": url, "ok": False}
    try:
        headers = {"Range": f"bytes=0-{HEAD_BYTES - 1}"}
        with session.get(url, headers=headers, stream=True, timeout=TIMEOUT) as response:
            result.update(
                status=response.status_code,
                content_type=response.headers.get("Content-Type"),
                etag=response.headers.get("ETag"),
                last_modified=response.headers.get("Last-Modified"),
            )
            if not response.ok:
                result["error"] = f"HTTP {response.status_code} {response.reason}"
                return result
            head = next(response.iter_content(chunk_size=HEAD_BYTES), b"")
        error = check_head(head, fmt, result.get("content_type") or "")
        if error:
            result["error"] = error
        else:
            result["ok"] = True
    except requests.exceptions.RequestException as ex:
        result["error"] = str(ex)
    return result


def check_cosmic_api(session: requests.Session) -> Dict[str, Any]:
    """The COSMIC API needs credentials; check that it answers with JSON."""
    url = Settings.COSMIC["HOSTNAME"]
    result: Dict[str, Any] = {"url": url, "ok": False}
    try:
        response = session.get(url, timeout=TIMEOUT)
        result.update(
            status=response.status_code, content_type=response.headers.get("Content-Type")
        )
        if response.status_code in COSMIC_API_UP_STATUSES and "json" in (
            result["content_type"] or ""
        ):
            result["ok"] = True
        else:
            result["error"] = f"unexpected response HTTP {response.status_code}"
    except requests.exceptions.RequestException as ex:
        result["error"] = str(ex)
    return result


def check_source(source: Source, session: requests.Session) -> Dict[str, Any]:
    """A source is ok if at least one of its URLs serves the expected file."""
    if source.key == "cosmic" and not source.urls:
        checks: List[Dict[str, Any]] = [check_cosmic_api(session)]
    else:
        checks = [check_url(session, url, source.fmt) for url in source.urls]
    return {
        "name": source.name,
        "required": source.required,
        "ok": any(check["ok"] for check in checks),
        "urls": checks,
    }


class CheckSources:
    """`fusion_report check-sources`: probe every remote source and report the results."""

    def __init__(self, params: Namespace) -> None:
        with make_session(params.no_ssl) as session:
            self.results = {
                key: check_source(source, session) for key, source in get_sources().items()
            }

        for result in self.results.values():
            for check in result["urls"]:
                status = "OK" if check["ok"] else f"BROKEN ({check.get('error')})"
                message = f"{result['name']}: {check['url']} -> {status}"
                (LOG.info if check["ok"] else LOG.warning)(message)

        if params.json:
            with open(params.json, "w", encoding="utf-8") as handle:
                json.dump(self.results, handle, indent=2, sort_keys=True)
                handle.write("\n")

        broken = [
            result["name"]
            for result in self.results.values()
            if not result["ok"] and (result["required"] or params.strict)
        ]
        if broken:
            raise DownloadException(f"Broken database source(s): {', '.join(broken)}")
        optional_broken = [r["name"] for r in self.results.values() if not r["ok"]]
        if optional_broken:
            LOG.warning(
                "All required database sources are available. Broken optional source(s): "
                f"{', '.join(optional_broken)}."
            )
        else:
            LOG.info("All database sources are available.")
