""" Helper class for Downloading all databases. """
import os
import sys
import base64
import subprocess
import urllib.request
from multiprocessing import Pool
import rapidjson

class Download:
    """
    Class designed for downloading any type of required database.
    Currently the script is able to download: Mitelman, FusionGDB and COSMIC with provided
    credentials.
    """
    def __init__(self, params):
        self.__params = ''
        self.__cosmic_token = ''
        self.__root_base = os.path.dirname(__file__)
        self.__validate(params)

    def __validate(self, params):
        """
        Method validating required input. In this case COSMIC credentials.

        Args:
            params (ArgumentParser)
        """
        self.__cosmic_token = params.cosmic_token
        if (
                self.__cosmic_token is None
                and (params.cosmic_usr is not None or params.cosmic_passwd is not None)
            ):
            self.__cosmic_token = base64.b64encode(
                f'{params.cosmic_usr}:{params.cosmic_passwd}'.encode()
            ).decode('utf-8')
        else:
            sys.exit('COSMIC credentials have not been provided correctly')

        # Making sure output directory exists
        if not os.path.exists(params.output):
            os.mkdir(params.output)

        self.__params = params

    def get_all_databases(self):
        """
        Method for downloading all databases in parallel.
        """
        # Change to update directory
        os.chdir(self.__params.output)
        commands = []
        commands.append(self.__get_fusiongdb())
        commands.append(self.__get_mitelman())
        commands.append(self.__get_cosmic())
        with Pool(3) as pool:
            pool.map(self.execute, commands)

        # cleanup
        self.execute(['rm *.dat *.tsv *.txt *.tar.gz *.sql'])

    def __get_fusiongdb(self):
        """
        Method for download FusionGDB database.

        Returns:
            commands (list): List of all required commands for execution
        """
        commands = []
        hostname = 'https://ccsm.uth.edu/FusionGDB/tables'
        urls = [
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

    def __get_mitelman(self):
        """
        Method for download Mitelman database.

        Returns:
            commands (list): List of all required commands for execution
        """
        commands = []
        url = 'ftp://ftp1.nci.nih.gov/pub/CGAP/mitelman.tar.gz'
        commands.append(f'wget {url}')
        commands.append(f'tar -xvzf mitelman.tar.gz')
        commands.append(
            "for db_file in *.dat; do \
            sed -n '1!p' $db_file > ${db_file%.*}_stripped.dat; done"
        )
        commands.append(
            f'sqlite3 mitelman.db < {os.path.join(self.__root_base, "../db/Mitelman.sql")}'
        )

        return commands

    def __get_cosmic(self):
        """
        Method for download COSMIC database.

        Returns:
            commands (list): List of all required commands for execution
        """
        commands = []
        hostname = 'https://cancer.sanger.ac.uk'
        url = f'{hostname}/cosmic/file_download/GRCh38/cosmic/v87/CosmicFusionExport.tsv.gz'
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Basic {self.__cosmic_token}')
        req.add_header(
            'User-Agent',
            '''Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)
            Chrome/41.0.2228.0 Safari/537.3'''
        )

        res = urllib.request.urlopen(req)
        parsed_res = rapidjson.loads(res.read().decode('utf-8'))
        commands.append(f'wget "{parsed_res["url"]}" -O CosmicFusionExport.tsv.gz')
        commands.append('gunzip CosmicFusionExport.tsv.gz')
        commands.append("sed -n '1!p' CosmicFusionExport.tsv > CosmicFusionExport_stripped.tsv")
        commands.append(f'sqlite3 cosmic.db < {os.path.join(self.__root_base, "../db/Cosmic.sql")}')

        return commands

    @staticmethod
    def execute(commands):
        """
        Method for executing a command in shell.

        Args:
            commands (list): List of commands to execute
        """
        try:
            for command in commands:
                subprocess.run(command, shell=True)
        except subprocess.CalledProcessError as error:
            sys.exit(error)
