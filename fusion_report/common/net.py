import base64
import glob
import gzip
import os
import shutil
import ssl
import urllib.error
import urllib.request
import time
import pandas as pd
from zipfile import ZipFile


from argparse import Namespace
from typing import List

import rapidjson

from fusion_report.common.exceptions.download import DownloadException
from fusion_report.common.logger import Logger
from fusion_report.data.cosmic import CosmicDB
from fusion_report.settings import Settings
from multiprocessing import Pool
from fusion_report.data.fusiongdb import FusionGDB
from fusion_report.data.fusiongdb2 import FusionGDB2
from fusion_report.data.mitelman import MitelmanDB

class Net:

    @staticmethod
    def get_cosmic_token(params: Namespace):
        if params.cosmic_token is not None:
            return params.cosmic_token

        if (
                params.cosmic_token is None
                and (params.cosmic_usr is not None or params.cosmic_passwd is not None)
        ):
            return base64.b64encode(
                f'{params.cosmic_usr}:{params.cosmic_passwd}'.encode()
            ).decode('utf-8')
        else:
            raise DownloadException('COSMIC credentials have not been provided correctly')

    @staticmethod
    def get_large_file(url: str, ignore_ssl: bool = False) -> None:
        """Method for downloading a large file."""

        ctx = None
        if ignore_ssl:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        if url.startswith('https') or url.startswith('ftp'):
            try:
                with urllib.request.urlopen(url, context=ctx) as response:
                    file = url.split('/')[-1].split('?')[0]
                    Logger(__name__).info('Downloading %s', file)
                    # only download if file size doesn't match
                    if not os.path.exists(file) or \
                            (response.info()['Content-Length'] or 0) != os.stat(file).st_size:
                        with open(file, 'wb') as out_file:
                            shutil.copyfileobj(response, out_file)
            except urllib.error.HTTPError as ex:
                raise DownloadException(ex)
        else:
            Logger(__name__).error('Downloading resources supports only HTTPS or FTP')

    @staticmethod
    def get_cosmic(token: str, return_err: List[str]) -> None:
        """Method for download COSMIC database."""

        # get auth url to download file
        files = []
        file: str = Settings.COSMIC["FILE"]
        url: str = f'{Settings.COSMIC["HOSTNAME"]}/{Settings.COSMIC["FILE"]}'
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Basic {token}')
        req.add_header(
            'User-Agent',
            '''Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)
            Chrome/41.0.2228.0 Safari/537.3'''
        )
        try:
            res = urllib.request.urlopen(req)
            auth_url: str = rapidjson.loads(res.read().decode('utf-8'))['url']
            Net.get_large_file(auth_url)

            files.append('.'.join(file.split('.')[:-1]))
            with gzip.open(file, 'rb') as archive, open(files[0], 'wb') as out_file:
                shutil.copyfileobj(archive, out_file)

            db = CosmicDB('.')
            db.setup(files, delimiter='\t', skip_header=True)
        except urllib.error.HTTPError as ex:
            return_err.append(f'{Settings.COSMIC["NAME"]}: {ex}')

    @staticmethod
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

    @staticmethod
    def get_fusiongdb2(self, return_err: List[str]) -> None:
        """Method for download FusionGDB2 database."""
        try:
            url: str = f'{Settings.FUSIONGDB2["HOSTNAME"]}/{Settings.FUSIONGDB2["FILE"]}'
            Net.get_large_file(url)
            file: str = f'{Settings.FUSIONGDB2["FILE"]}'
            df = pd.read_excel(file, engine='openpyxl')
            df["fusion"] = df["5'-gene (text format)"] + "--" + df["3'-gene (text format)"]
            file_csv = 'fusionGDB2.csv'
            df['fusion'].to_csv(file_csv, header=False, index=False, sep=',', encoding='utf-8')

            db = FusionGDB2('.')
            db.setup([file_csv], delimiter=',', skip_header=False)

        except DownloadException as ex:
            return_err.append(f'FusionGDB2: {ex}')

    @staticmethod
    def get_mitelman(self, return_err: List[str]) -> None:
        """Method for download Mitelman database."""
        try:
            url: str = f'{Settings.MITELMAN["HOSTNAME"]}/{Settings.MITELMAN["FILE"]}'
            Net.get_large_file(url)
            with ZipFile(Settings.MITELMAN['FILE'], 'r') as archive:
                files = [x for x in archive.namelist() if "MBCA.TXT.DATA" in x]
                archive.extractall()

            db = MitelmanDB('.')
            db.setup(files, delimiter='\t', skip_header=False, encoding='ISO-8859-1')
        except DownloadException as ex:
            return_err.append(f'Mitelman: {ex}')

    @staticmethod
    def clean():
        """Remove all files except *db."""
        for temp in glob.glob('*/'):
            shutil.rmtree(temp)
        for temp in glob.glob('*[!.db]'):
            if not os.path.isdir(temp):
                os.remove(temp)

    @staticmethod
    def timestamp():
        """Create a timestamp file at DB creation"""
        timestr = time.strftime("%Y-%m-%d/%H:%M")
        text_file = open("DB-timestamp.txt", "w")
        text_file.write(timestr)
        text_file.close()
