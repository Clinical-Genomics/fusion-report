""" Download module """
import os

from argparse import Namespace
from typing import List

from fusion_report.common.exceptions.download import DownloadException
from fusion_report.common.logger import Logger
from fusion_report.common.net import Net

class Download:
    """Class designed for downloading any type of required database.
    Currently the script is able to download: Mitelman, FusionGDB and COSMIC with provided
    credentials.

    Attributes:
        cosmic_token: Auth token for downloading COSMIC database
    """

    def __init__(self, params: Namespace):
        self.validate(params)
        self.download_all(params)

    def validate(self, params: Namespace) -> None:
        """Method validating required input. In this case COSMIC credentials."""
        self.cosmic_token = Net.get_cosmic_token(params)

        # making sure output directory exists
        if not os.path.exists(params.output):
            os.makedirs(params.output, 0o755)

    def download_all(self, params: Namespace) -> None:
        """Download all databases."""
        return_err: List[str] = []
        os.chdir(params.output)

        # MITELMAN
        Net.get_mitelman(self, return_err)

        # FusionGDB
        Net.get_fusiongdb(self, return_err)

        # FusionGDB2
        Net.get_fusiongdb2(self, return_err)

        # COSMIC
        if params.qiagen:
            Logger(__name__).info('Downloading resources from QIAGEN...')
            Net.get_cosmic_from_qiagen(self.cosmic_token, return_err)
        else:
            Logger(__name__).info('Downloading resources from SANGER...')
            Net.get_cosmic_from_sanger(self.cosmic_token, return_err)

        if len(return_err) > 0:
            raise DownloadException(return_err)

        Logger(__name__).info('Downloading finished')
        Net.clean()

        # Create timestamp:
        Net.timestamp()
