""" Download module """
import base64
import glob
import gzip
import os
import shutil
import ssl
import tarfile
import urllib.error
import urllib.request
from argparse import Namespace
from multiprocessing import Manager, Pool, Process
from typing import List

import rapidjson

from fusion_report.common.exceptions.download import DownloadException
from fusion_report.common.logger import Logger
from fusion_report.data.cosmic import CosmicDB
from fusion_report.data.fusiongdb import FusionGDB
from fusion_report.data.mitelman import MitelmanDB


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
        self.cosmic_token: str = params.cosmic_token
        if (
                self.cosmic_token is None
                and (params.cosmic_usr is not None or params.cosmic_passwd is not None)
        ):
            self.cosmic_token = base64.b64encode(
                f'{params.cosmic_usr}:{params.cosmic_passwd}'.encode()
            ).decode('utf-8')
        else:
            raise DownloadException('COSMIC credentials have not been provided correctly')

        # making sure output directory exists
        if not os.path.exists(params.output):
            os.makedirs(params.output, 0o755)

    def download_all(self, params: Namespace) -> None:
        """Parallel downloading of all databases."""
        # change to update directory
        os.chdir(params.output)
        return_err: List[str] = Manager().list()

        processes = [
            Process(name='FusionGDB', target=self.get_fusiongdb, args=(return_err,)),
            Process(name='Mitelman', target=self.get_mitelman, args=(return_err,)),
            Process(name='COSMIC', target=self.get_cosmic, args=(return_err,))
        ]

        for process in processes:
            process.start()

        for process in processes:
            process.join()

        if len(return_err) > 0:
            raise DownloadException(return_err)

        Logger(__name__).info('Cleaning up the mess')
        self.clean()

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

    def get_fusiongdb(self, return_err: List[str]) -> None:
        """Method for download FusionGDB database."""

        hostname: str = 'https://ccsm.uth.edu/FusionGDB/tables'
        files: List[str] = [
            'TCGA_ChiTaRS_combined_fusion_information_on_hg19.txt',
            'TCGA_ChiTaRS_combined_fusion_ORF_analyzed_gencode_h19v19.txt',
            'uniprot_gsymbol.txt',
            'fusion_uniprot_related_drugs.txt',
            'fusion_ppi.txt',
            'fgene_disease_associations.txt'
        ]

        pool = Pool(4)
        pool.starmap(self.get_large_file, [(f'{hostname}/{x}', True) for x in files])
        pool.close()
        pool.join()
        db = FusionGDB('.')
        db.setup(files, delimiter='\t', skip_header=False)

    def get_mitelman(self, return_err: List[str]) -> None:
        """Method for download Mitelman database."""
        try:
            file: str = 'mitelman.tar.gz'
            url: str = f'ftp://ftp1.nci.nih.gov/pub/CGAP/{file}'
            self.get_large_file(url)

            with tarfile.open(file) as archive:
                files = archive.getnames()
                archive.extractall()

            db = MitelmanDB('.')
            db.setup(files, delimiter='\t', skip_header=True, encoding='ISO-8859-1')
        except DownloadException as ex:
            return_err.append(f'Mitelman: {ex}')

    def get_cosmic(self, return_err: List[str]) -> None:
        """Method for download COSMIC database."""

        files = []
        file: str = 'CosmicFusionExport.tsv.gz'
        url: str = 'https://cancer.sanger.ac.uk/cosmic/file_download/GRCh38/cosmic/v87/'

        # get auth url to download file
        req = urllib.request.Request(f'{url}{file}')
        req.add_header('Authorization', f'Basic {self.cosmic_token}')
        req.add_header(
            'User-Agent',
            '''Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)
            Chrome/41.0.2228.0 Safari/537.3'''
        )
        try:
            res = urllib.request.urlopen(req)
            auth_url: str = rapidjson.loads(res.read().decode('utf-8'))['url']
            self.get_large_file(auth_url)

            files.append('.'.join(file.split('.')[:-1]))
            with gzip.open(file, 'rb') as archive, open(files[0], 'wb') as out_file:
                shutil.copyfileobj(archive, out_file)

            db = CosmicDB('.')
            db.setup(files, delimiter='\t', skip_header=True)
        except urllib.error.HTTPError as ex:
            return_err.append(f'COSMIC: {ex}')

    @staticmethod
    def clean():
        """Remove all files except *db."""
        for temp in glob.glob('*[!db]'):
            os.remove(temp)
