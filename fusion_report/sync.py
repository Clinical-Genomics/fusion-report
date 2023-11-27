""" Sync module """
import os
import time

from argparse import Namespace
from multiprocessing import Manager, Process
from typing import List

from fusion_report.common.exceptions.download import DownloadException
from fusion_report.common.logger import Logger
from fusion_report.common.net import Net

from fusion_report.settings import Settings


class Sync:
    def __init__(self, params: Namespace):
        self.cosmic_token = Net.get_cosmic_token(params)

        # making sure output directory exists
        if not os.path.exists(params.output):
            os.makedirs(params.output, 0o755)

        os.chdir(params.output)
        return_err: List[str] = Manager().list()

        processes = [
            Process(
                name=Settings.MITELMAN["NAME"],
                target=Net.get_mitelman,
                args=(return_err,),
            ),
            Process(
                name=Settings.COSMIC["NAME"],
                target=Net.get_cosmic,
                args=(
                    self.cosmic_token,
                    return_err,
                ),
            ),
            Process(
                name=Settings.FUSIONGDB2["NAME"],
                target=Net.get_fusiongdb2,
                args=(return_err,),
            ),
        ]

        for process in processes:
            process.start()

        for process in processes:
            process.join()

        if len(return_err) > 0:
            raise DownloadException(return_err)

        time.sleep(1)
        Logger(__name__).info("Cleaning up the mess")
        Net.clean()
