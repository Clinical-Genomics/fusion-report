""" Sync module """
import os
import tarfile
import time

from argparse import Namespace
from multiprocessing import Manager, Pool, Process
from typing import List

from fusion_report.common.exceptions.download import DownloadException
from fusion_report.common.logger import Logger
from fusion_report.common.net import Net
from fusion_report.data.fusiongdb import FusionGDB
from fusion_report.data.mitelman import MitelmanDB
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
            Process(name=Settings.FUSIONGDB['NAME'], target=self.get_fusiongdb, args=(return_err,)),
            Process(name=Settings.MITELMAN['NAME'], target=self.get_mitelman, args=(return_err,)),
            Process(name=Settings.COSMIC['NAME'], target=Net.get_cosmic, args=(self.cosmic_token, return_err,))
        ]

        for process in processes:
            process.start()

        for process in processes:
            process.join()

        if len(return_err) > 0:
            raise DownloadException(return_err)

        time.sleep(1)
        Logger(__name__).info('Cleaning up the mess')
        Net.clean()

    def get_fusiongdb(self, return_err: List[str]) -> None:
        """Method for download FusionGDB database."""

        pool_params = [
            (f'{Settings.FUSIONGDB["HOSTNAME"]}/{x}', True) for x in Settings.FUSIONGDB["FILES"]
        ]
        pool = Pool(Settings.THREAD_NUM)
        pool.starmap(Net.get_large_file, pool_params)
        pool.close()
        pool.join()
        db = FusionGDB('.')
        db.setup(Settings.FUSIONGDB['FILES'], delimiter='\t', skip_header=False)

    def get_mitelman(self, return_err: List[str]) -> None:
        """Method for download Mitelman database."""
        try:
            url: str = f'{Settings.MITELMAN["HOSTNAME"]}/{Settings.MITELMAN["FILE"]}'
            Net.get_large_file(url)

            with tarfile.open(Settings.MITELMAN['FILE']) as archive:
                files = archive.getnames()
                archive.extractall()

            db = MitelmanDB('.')
            db.setup(files, delimiter='\t', skip_header=True, encoding='ISO-8859-1')
        except DownloadException as ex:
            return_err.append(f'Mitelman: {ex}')
