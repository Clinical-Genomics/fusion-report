"""Registry of remote database sources.

One place that describes every database fusion-report can download: where it comes from
(ordered mirrors), what the file looks like (format, checksum) and whether `download` must
fail when it is unavailable. It is built from `Settings` on each call, so `Settings.COSMIC`,
`Settings.MITELMAN`, `Settings.FUSIONGDB2` and `Settings.MIRRORS` stay the single place to
configure URLs and remain backwards compatible.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from fusion_report.settings import Settings


@dataclass(frozen=True)
class Source:
    """A remote database source.

    Attributes:
        key: lower-case identifier, used in CLI flags (`--no-<key>`) and the `<key>.db` file
        name: display name, as used in reports and database classes
        required: if True, `download` fails when this source cannot be fetched
        weight: weight in the Fusion Indication Index
        version: data version (informational, recorded in the manifest)
        filename: name of the downloaded file
        fmt: expected file format, see `fusion_report.common.fetch.check_magic`
        urls: download URLs, tried in order (primary first, then mirrors)
        sha256: expected checksum of the downloaded file, if the data is frozen
        homepage: where users can find the data manually
    """

    key: str
    name: str
    required: bool
    weight: float
    version: str
    filename: str
    fmt: str
    urls: List[str] = field(default_factory=list)
    sha256: Optional[str] = None
    homepage: str = ""


def _urls(settings: Dict[str, str], key: str) -> List[str]:
    return [f'{settings["HOSTNAME"]}/{settings["FILE"]}', *Settings.MIRRORS.get(key, [])]


def get_sources() -> Dict[str, Source]:
    """Return all known sources, keyed by `Source.key`."""
    return {
        "cosmic": Source(
            key="cosmic",
            name=Settings.COSMIC["NAME"],
            required=True,
            weight=Settings.FUSION_WEIGHTS["cosmic"],
            version=Settings.COSMIC["VERSION"],
            filename=Settings.COSMIC["TARFILE"],
            fmt="tar",
            # COSMIC files are served from pre-signed URLs requested from the Sanger API
            urls=list(Settings.MIRRORS.get("cosmic", [])),
            homepage=Settings.COSMIC.get("HOMEPAGE", ""),
        ),
        "mitelman": Source(
            key="mitelman",
            name=Settings.MITELMAN["NAME"],
            required=True,
            weight=Settings.FUSION_WEIGHTS["mitelman"],
            version=Settings.MITELMAN.get("VERSION", ""),
            filename=Settings.MITELMAN["FILE"],
            fmt="zip",
            urls=_urls(Settings.MITELMAN, "mitelman"),
            homepage=Settings.MITELMAN.get("HOMEPAGE", ""),
        ),
        "fusiongdb2": Source(
            key="fusiongdb2",
            name=Settings.FUSIONGDB2["NAME"],
            required=False,
            weight=Settings.FUSION_WEIGHTS["fusiongdb2"],
            version=Settings.FUSIONGDB2.get("VERSION", ""),
            filename=Settings.FUSIONGDB2["FILE"],
            fmt="text",
            urls=_urls(Settings.FUSIONGDB2, "fusiongdb2"),
            sha256=Settings.FUSIONGDB2.get("SHA256"),
            homepage=Settings.FUSIONGDB2.get("HOMEPAGE", ""),
        ),
    }


def get_source(key: str) -> Source:
    """Return the source with the given key (cosmic, mitelman, fusiongdb2)."""
    return get_sources()[key]
