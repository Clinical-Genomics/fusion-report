"""Provenance manifest (`db_manifest.json`) written next to the databases.

Records, per source, whether it was built, skipped or failed, where the data came from
(URL or local file), its checksum, size, version and row count. `run` reads it to know which
databases to expect and logs where they came from.
"""

import hashlib
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

from fusion_report.common.logger import Logger
from fusion_report.settings import Settings

LOG = Logger(__name__)

MANIFEST_FILE = "db_manifest.json"
SECRET_FLAGS = ("--cosmic_usr", "--cosmic_passwd", "--cosmic_token")

OK = "ok"
FAILED = "failed"
SKIPPED = "skipped"  # optional source that could not be built
DISABLED = "disabled"  # turned off with --no-<db>


def redact(argv: List[str]) -> List[str]:
    """Replace COSMIC credentials in a command line with `***`."""
    redacted: List[str] = []
    hide_next = False
    for arg in argv:
        if hide_next:
            redacted.append("***")
            hide_next = False
        elif arg in SECRET_FLAGS:
            redacted.append(arg)
            hide_next = True
        elif arg.split("=", 1)[0] in SECRET_FLAGS:
            redacted.append(f"{arg.split('=', 1)[0]}=***")
        else:
            redacted.append(arg)
    return redacted


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class Manifest:
    """Collects per-source provenance and writes `db_manifest.json`."""

    def __init__(self, command: str) -> None:
        self.data: Dict[str, Any] = {
            "fusion_report_version": Settings.VERSION,
            "command": command,
            "argv": redact(sys.argv[1:]),
            "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "sources": {},
        }

    def record(self, source, status: str, required: bool, **details: Any) -> None:
        """Record the outcome for a registry `Source` (or anything with key/name/version)."""
        self.data["sources"][source.key] = {
            "name": source.name,
            "status": status,
            "required": required,
            "version": source.version,
            "db_file": f"{source.name.lower()}.db" if status == OK else None,
            **details,
        }

    def record_file(self, source, path: str, origin: str, rows: int, **details: Any) -> None:
        """Record a successfully built source with checksum and size of its input file."""
        exists = os.path.isfile(path)
        self.record(
            source,
            OK,
            required=details.pop("required", source.required),
            origin=origin,
            sha256=file_sha256(path) if exists else None,
            bytes=os.path.getsize(path) if exists else None,
            rows=rows,
            **details,
        )

    def write(self, output_dir: str) -> str:
        path = os.path.join(output_dir, MANIFEST_FILE)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.data, handle, indent=2, sort_keys=True)
            handle.write("\n")
        return path


def read_manifest(db_path: str) -> Optional[Dict[str, Any]]:
    """Return the manifest in `db_path`, or None if there is none (older database folders)."""
    path = os.path.join(db_path, MANIFEST_FILE)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as ex:
        LOG.warning(f"Could not read {path}: {ex}")
        return None
