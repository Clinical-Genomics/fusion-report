""" Helper class for Downloading all databases. """
import os
import base64
import subprocess
import urllib.request
from typing import List
from pathlib import Path
from multiprocessing import Pool
import rapidjson
from fusion_report.common.exceptions.download import DownloadException

class Download:
    """
    Class designed for downloading any type of required database.
    Currently the script is able to download: Mitelman, FusionGDB and COSMIC with provided
    credentials.
    """
    def __init__(self, params):
        self.__root_base: str = os.path.dirname(__file__)
        self.__validate(params)
        self.__get_all()

    def __validate(self, params) -> None:
        """
        Method validating required input. In this case COSMIC credentials.

        Args:
            params (argparse.Namespace)
        """
        self.__cosmic_token: str = params.cosmic_token
        if (
                self.__cosmic_token is None
                and (params.cosmic_usr is not None or params.cosmic_passwd is not None)
            ):
            self.__cosmic_token: str = base64.b64encode(
                f'{params.cosmic_usr}:{params.cosmic_passwd}'.encode()
            ).decode('utf-8')
        else:
            raise DownloadException('COSMIC credentials have not been provided correctly')

        # Making sure output directory exists
        if not Path(params.output).exists():
            Path(params.output).mkdir(parents=True, exist_ok=True)

        self.__params = params

    def __get_all(self) -> None:
        """
        Method for downloading all databases in parallel.
        """
        # Change to update directory
        os.chdir(self.__params.output)
        commands: List[List[str]] = [
            self.__get_fusiongdb(),
            self.__get_mitelman(),
            self.__get_cosmic()
        ]
        with Pool(len(commands)) as pool:
            pool.map(self.execute, commands)

        # cleanup
        self.execute(['rm *.dat *.tsv *.txt *.tar.gz *.sql'])

    def __get_fusiongdb(self) -> List[str]:
        """
        Method for download FusionGDB database.

        Returns:
            commands (list): List of all required commands for execution
        """
        commands: List[str] = []
        hostname: str = 'https://ccsm.uth.edu/FusionGDB/tables'
        urls: List[str] = [
            f'{hostname}/TCGA_ChiTaRS_combined_fusion_information_on_hg19.txt',
            f'{hostname}/TCGA_ChiTaRS_combined_fusion_ORF_analyzed_gencode_h19v19.txt',
            f'{hostname}/uniprot_gsymbol.txt',
            f'{hostname}/fusion_uniprot_related_drugs.txt',
            f'{hostname}/fusion_ppi.txt',
            f'{hostname}/fgene_disease_associations.txt'
        ]

        for url in urls:
            commands.append(f'wget --no-check-certificate {url}')

        commands.append(
            f'sqlite3 fusiongdb.db < {os.path.join(self.__root_base, "../db/FusionGDB.sql")}'
        )

        return commands

    def __get_mitelman(self) -> List[str]:
        """
        Method for download Mitelman database.

        Returns:
            commands (list): List of all required commands for execution
        """
        return [
            f'wget ftp://ftp1.nci.nih.gov/pub/CGAP/mitelman.tar.gz',
            f'tar -xvzf mitelman.tar.gz',
            "for db_file in *.dat; do sed -n '1!p' $db_file > ${db_file%.*}_stripped.dat; done",
            f'sqlite3 mitelman.db < {os.path.join(self.__root_base, "../db/Mitelman.sql")}'
        ]

    def __get_cosmic(self) -> List[str]:
        """
        Method for download COSMIC database.

        Returns:
            commands (list): List of all required commands for execution
        """
        hostname: str = 'https://cancer.sanger.ac.uk'
        url: str = f'{hostname}/cosmic/file_download/GRCh38/cosmic/v87/CosmicFusionExport.tsv.gz'
        req = urllib.request.Request(url)

        req.add_header('Authorization', f'Basic {self.__cosmic_token}')
        req.add_header(
            'User-Agent',
            '''Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)
            Chrome/41.0.2228.0 Safari/537.3'''
        )

        res = urllib.request.urlopen(req)
        auth_url: str = rapidjson.loads(res.read().decode('utf-8'))['url']

        return [
            f'wget "{auth_url}" -O CosmicFusionExport.tsv.gz',
            'gunzip CosmicFusionExport.tsv.gz',
            "sed -n '1!p' CosmicFusionExport.tsv > CosmicFusionExport_stripped.tsv",
            f'sqlite3 cosmic.db < {os.path.join(self.__root_base, "../db/Cosmic.sql")}'
        ]

    @staticmethod
    def execute(commands: List[str]) -> None:
        """
        Method for executing a command in shell.

        Args:
            commands (list): List of commands to execute
        """
        try:
            for command in commands:
                subprocess.run(command, shell=True)
        except subprocess.CalledProcessError as ex:
            raise DownloadException(ex)
