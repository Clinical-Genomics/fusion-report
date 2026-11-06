"""Download module"""

import os
from argparse import Namespace
from typing import Any, Callable, Dict, List, Optional

from fusion_report.common import db_builders
from fusion_report.common.exceptions.download import DownloadException
from fusion_report.common.fetch import download_source
from fusion_report.common.logger import Logger
from fusion_report.common.manifest import DISABLED, FAILED, SKIPPED, Manifest
from fusion_report.common.net import Net
from fusion_report.data.sources import Source, get_source

LOG = Logger(__name__)

SKIPPED_HINT = (
    "{name} is optional and was skipped. Use --no-{key} to silence this warning, provide a "
    "local copy with --{key}-file <file>, or build it with "
    "`fusion_report createdb <output> --{key} <file>`."
)


class Download:
    """Class designed for downloading any type of required database.
    Currently the script is able to download: Mitelman, FusionGDB2 and COSMIC with provided
    credentials.

    Each source is processed independently, so one failing source does not stop the others.
    COSMIC and Mitelman are required (unless disabled with --no-*), FusionGDB2 is optional: if it
    fails, a warning is logged and the remaining databases are still written. With
    --allow-missing every source is optional. Every source can also be built from a local file
    (--<db>-file) or downloaded from another URL (--<db>-url). The outcome per source is recorded
    in `db_manifest.json`.

    Attributes:
        cosmic_token: Auth token for downloading COSMIC database
    """

    def __init__(self, params: Namespace):
        self.download_all(params)

    def validate(self, params: Namespace) -> None:
        """Method validating required input. In this case COSMIC credentials."""
        if params.qiagen:
            self.cosmic_token = Net.get_cosmic_qiagen_token(params)
        else:
            self.cosmic_token = Net.get_cosmic_token(params)

    def download_all(self, params: Namespace) -> None:
        """Download all databases."""
        original_cwd = os.getcwd()
        output_dir = os.path.abspath(params.output)
        # resolve local files before changing directory
        local_files = {
            key: os.path.abspath(path) if path else None
            for key in ("mitelman", "fusiongdb2", "cosmic")
            for path in [getattr(params, f"{key}_file", None)]
        }
        allow_missing = getattr(params, "allow_missing", False)

        # making sure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, 0o755)

        return_err: List[str] = []
        manifest = Manifest("download")
        built = 0
        tmp_dir = os.path.join(output_dir, "tmp_dir")
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        os.chdir(tmp_dir)

        fetchers: Dict[str, Callable[[Source, Namespace, Optional[str]], Dict[str, Any]]] = {
            "mitelman": self._fetch_mitelman,
            "fusiongdb2": self._fetch_fusiongdb2,
            "cosmic": self._fetch_cosmic,
        }
        try:
            for key, fetch in fetchers.items():
                source = get_source(key)
                required = source.required and not allow_missing
                if getattr(params, f"no_{key}"):
                    manifest.record(source, DISABLED, required=False)
                    continue
                try:
                    details = fetch(source, params, local_files[key])
                    manifest.record_file(source, required=required, **details)
                    built += 1
                except Exception as ex:
                    message = str(ex)
                    if not message.startswith(f"{source.name}:"):
                        message = f"{source.name}: {message}"
                    if required:
                        manifest.record(source, FAILED, required=True, error=message)
                        return_err.append(message)
                    else:
                        manifest.record(source, SKIPPED, required=False, error=message)
                        hint = SKIPPED_HINT.format(name=source.name, key=key)
                        LOG.warning(f"{message}\n{hint}")

            if return_err:
                raise DownloadException("\n".join(return_err))
            attempted = [s for s in manifest.data["sources"].values() if s["status"] != DISABLED]
            if attempted and built == 0:
                raise DownloadException("No database could be downloaded or built.")

            LOG.info("Downloading finished")
            Net.timestamp(output_dir)
        finally:
            os.chdir(original_cwd)
            Net.clean(tmp_dir, output_dir)
            manifest.write(output_dir)

    @staticmethod
    def _download_or_local(
        source: Source, params: Namespace, local_file: Optional[str]
    ) -> Dict[str, Any]:
        """Return the input file for a source: the local file if given, otherwise download it
        (from --<db>-url if given, else from the registry URLs)."""
        if local_file:
            if not os.path.isfile(local_file):
                raise FileNotFoundError(f"local file not found: {local_file}")
            LOG.info(f"Using local {source.name} file {local_file}")
            return {"path": local_file, "origin": f"file:{local_file}"}
        url = getattr(params, f"{source.key}_url", None)
        used = download_source(
            source, source.filename, no_ssl=params.no_ssl, urls=[url] if url else None
        )
        # never record query strings (signed URLs, tokens) in the manifest
        return {"path": source.filename, "origin": used.split("?")[0]}

    def _fetch_mitelman(self, source, params, local_file) -> Dict[str, Any]:
        details = self._download_or_local(source, params, local_file)
        details["rows"] = db_builders.build_mitelman(details["path"])
        return details

    def _fetch_fusiongdb2(self, source, params, local_file) -> Dict[str, Any]:
        details = self._download_or_local(source, params, local_file)
        details["rows"] = db_builders.build_fusiongdb2(details["path"])
        return details

    def _fetch_cosmic(self, source, params, local_file) -> Dict[str, Any]:
        if local_file:
            details = self._download_or_local(source, params, local_file)
            details["rows"] = db_builders.build_cosmic(details["path"])
            return details

        self.validate(params)
        errors: List[str] = []
        output_dir = os.path.abspath(params.output)
        if params.qiagen:
            LOG.info("Downloading resources from QIAGEN...")
            Net.get_cosmic_from_qiagen(self.cosmic_token, errors, output_dir, params.no_ssl)
            origin = "qiagen"
        else:
            LOG.info("Downloading resources from SANGER...")
            Net.get_cosmic_from_sanger(self.cosmic_token, errors, params.no_ssl, output_dir)
            origin = "sanger"
        if errors:
            raise DownloadException("\n".join(errors))
        path = db_builders.COSMIC_TABLE_FILE
        rows = db_builders.count_rows(path, skip_header=True) if os.path.isfile(path) else None
        return {"path": path, "origin": origin, "rows": rows}
