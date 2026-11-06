"""Download module"""

import os
from argparse import Namespace
from typing import List

from fusion_report.common.exceptions.download import DownloadException
from fusion_report.common.logger import Logger
from fusion_report.common.net import Net

LOG = Logger(__name__)

FUSIONGDB2_SKIPPED_HINT = (
    "FusionGDB2 is optional (it does not affect the Fusion Indication Index) and was skipped. "
    "Use --no-fusiongdb2 to silence this warning, or build it from a local copy with "
    "`fusion_report createdb <output> --fusiongdb2 <file>`."
)


class Download:
    """Class designed for downloading any type of required database.
    Currently the script is able to download: Mitelman, FusionGDB2 and COSMIC with provided
    credentials.

    Each source is downloaded independently, so one failing source does not stop the others.
    COSMIC and Mitelman are required (unless disabled with --no-*), FusionGDB2 is optional: if it
    fails, a warning is logged and the remaining databases are still written.

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
        original_cwd = os.getcwd()
        output_dir = os.path.abspath(params.output)

        # making sure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, 0o755)

        """Download all databases."""
        return_err: List[str] = []
        tmp_dir = os.path.join(output_dir, "tmp_dir")
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        os.chdir(tmp_dir)

        try:
            if not params.no_mitelman:
                # MITELMAN
                Net.get_mitelman(self, return_err, params.no_ssl)

            if not params.no_fusiongdb2:
                # FusionGDB2 (optional: failures are reported as warnings)
                optional_err: List[str] = []
                Net.get_fusiongdb2(self, optional_err, params.no_ssl)
                for err in optional_err:
                    LOG.warning(f"{err}\n{FUSIONGDB2_SKIPPED_HINT}")

            if not params.no_cosmic:
                # COSMIC
                self.validate(params)
                if params.qiagen:
                    LOG.info("Downloading resources from QIAGEN...")
                    Net.get_cosmic_from_qiagen(
                        self.cosmic_token, return_err, output_dir, params.no_ssl
                    )
                else:
                    LOG.info("Downloading resources from SANGER...")
                    Net.get_cosmic_from_sanger(
                        self.cosmic_token, return_err, params.no_ssl, output_dir
                    )

            if len(return_err) > 0:
                raise DownloadException("\n".join(return_err))

            LOG.info("Downloading finished")
            Net.timestamp(output_dir)
        finally:
            os.chdir(original_cwd)
            Net.clean(tmp_dir, output_dir)
