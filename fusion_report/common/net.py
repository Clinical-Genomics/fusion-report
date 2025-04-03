import base64
import glob
import gzip
import os
import shutil
import tarfile
import requests
import time
import pandas as pd
from zipfile import ZipFile
import subprocess
import json
from argparse import Namespace
from typing import List

from fusion_report.common.exceptions.download import DownloadException
from fusion_report.common.logger import Logger
from fusion_report.data.cosmic import CosmicDB
from fusion_report.settings import Settings
from fusion_report.data.fusiongdb2 import FusionGDB2
from fusion_report.data.mitelman import MitelmanDB

LOG = Logger(__name__)


class Net:
    @staticmethod
    def get_cosmic_token(params: Namespace):
        if params.cosmic_token is not None:
            return params.cosmic_token

        if params.cosmic_usr is not None and params.cosmic_passwd is not None:
            return base64.b64encode(f"{params.cosmic_usr}:{params.cosmic_passwd}".encode()).decode(
                "utf-8"
            )
        else:
            raise DownloadException("COSMIC credentials have not been provided correctly")

    @staticmethod
    def run_qiagen_cmd(cmd, return_output=False, silent=False):
        if not silent:
            print(cmd)
        if return_output:
            output = subprocess.check_output(cmd, shell=True, executable="/bin/bash").strip()
            return output
        else:
            subprocess.check_call(cmd, shell=True, executable="/bin/bash")

    @staticmethod
    def get_qiagen_files(token: str, output_path: str):
        files_request = (
            "curl --stderr -s -X GET "
            '-H "Content-Type: application/octet-stream" '
            '-H "Authorization: Bearer {token}" '
            '"https://my.qiagendigitalinsights.com/bbp/data/files/cosmic"'
            " -o {output_path}qiagen_files.tsv"
        )
        cmd = files_request.format(token=token, output_path=output_path)
        return Net.run_qiagen_cmd(cmd, True, True)

    @staticmethod
    def download_qiagen_file(token: str, file_id: str, output_path: str):
        file_request = (
            "curl -s -X GET "
            '-H "Content-Type: application/octet-stream" '
            '-H "Authorization: Bearer {token}" '
            '"https://my.qiagendigitalinsights.com/bbp/data/download/cosmic-download?name={file_id}"'
            " -o {output_path}Cosmic_Fusion_v101_GRCh38.tsv.gz"
        )
        cmd = file_request.format(token=token, file_id=file_id, output_path=output_path)
        Net.run_qiagen_cmd(cmd, True, True)

    @staticmethod
    def fetch_fusion_file_id(output_path: str):
        df = pd.read_csv(
            output_path + "/qiagen_files.tsv",
            names=["file_id", "file_name", "genome_draft"],
            sep="\t",
        )
        file_id = df.loc[
            (df["file_name"] == Settings.COSMIC["FILE"]) & (df["genome_draft"] == "cosmic/GRCh38"),
            "file_id",
        ].values[0]
        return file_id

    @staticmethod
    def get_cosmic_qiagen_token(params: Namespace):
        token_request = (
            "curl -s -X POST "
            '-H "Content-Type: application/x-www-form-urlencoded" '
            '-d "grant_type=password&client_id=603912630-14192122372034111918-SmRwso&username={uid}&password={pwd}" '
            '"https://apps.ingenuity.com/qiaoauth/oauth/token"'
        )
        cmd = token_request.format(uid=params.cosmic_usr, pwd=params.cosmic_passwd)
        token_response = Net.run_qiagen_cmd(cmd, True, True).decode("UTF-8")
        return json.loads(token_response)["access_token"]

    @staticmethod
    def get_large_file(url: str, no_ssl) -> None:
        """Method for downloading a large file."""
        LOG.info(f"Downloading {url}")
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, stream=True, verify=no_ssl)
            file = url.split("/")[-1].split("?")[0]

            if (
                not os.path.exists(file)
                or (response.headers.get("Content-Length") or 0) != os.stat(file).st_size
            ):
                with open(file, "wb") as out_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            out_file.write(chunk)
        except Exception as ex:
            LOG.error(f"Error downloading {url}, {ex}")
            raise DownloadException(ex)

    @staticmethod
    def get_cosmic_from_sanger_url(token: str, file_path: str) -> str:
        """Method for download COSMIC database from sanger website."""
        params = {"path": file_path, "bucket": "downloads"}
        url = Settings.COSMIC["HOSTNAME"]
        headers = {"Authorization": f"Basic {token}"}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("url")

    @staticmethod
    def extract_gz(file_path: str) -> str | None:
        """Decompresses a .gz file."""
        try:
            output_file = file_path.rsplit(".", 1)[0]  # Remove .gz extension
            with gzip.open(file_path, "rb") as f_in, open(output_file, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            LOG.info(f"Decompressed {file_path} to {output_file}")
            return output_file
        except Exception as e:
            LOG.error(f"Error extracting gzip file: {e}")
            return None

    @staticmethod
    def extract_tar(file_path: str, extract_to: str) -> str | None:
        """Extracts a specific file from a tar archive."""
        try:
            with tarfile.open(file_path, "r:") as tar:
                # Find the specific file
                target_file = "Cosmic_Fusion_v101_GRCh38.tsv.gz"
                if target_file in tar.getnames():
                    tar.extract(target_file, path=extract_to)
                    extracted_path = os.path.join(extract_to, target_file)
                    LOG.info(f"Extracted {target_file} to {extracted_path}")
                    return extracted_path
                else:
                    LOG.error(f"{target_file} not found in the tar archive.")
                    return None
        except Exception as e:
            LOG.error(f"Error extracting tar file: {e}")
            return None

    @staticmethod
    def get_cosmic_from_sanger(token: str, return_err: List[str], no_ssl, outputpath) -> None:
        """Downloads the COSMIC database from the Sanger website."""
        file_name = "grch38/cosmic/v101/" + Settings.COSMIC["TARFILE"]
        file_path = f"{file_name}"
        try:
            download_url = Net.get_cosmic_from_sanger_url(token, file_path=file_path)

            if not download_url:
                raise ValueError("Failed to retrieve the download URL.")

            LOG.info(f"Download URL: {download_url}")
            Net.get_large_file(download_url, no_ssl)
            Net.extract_tar(Settings.COSMIC["TARFILE"], ".")
            extracted_file = Net.extract_gz("." + "/" + Settings.COSMIC["FILE"])
            db = CosmicDB(".")
            db.setup([extracted_file.split("/")[-1]], delimiter="\t", skip_header=False)

        except requests.exceptions.RequestException as req_err:
            return_err.append(f'{Settings.COSMIC["NAME"]}: {req_err}')
        except (ValueError, KeyError) as json_err:
            return_err.append(f"Error processing request: {json_err}")

    @staticmethod
    def get_cosmic_from_qiagen(token: str, return_err: List[str], outputpath: str) -> None:
        """Method for download COSMIC database from QIAGEN."""
        try:
            Net.get_qiagen_files(token, outputpath)
        except Exception as ex:
            LOG.info(ex)

        file_id = Net.fetch_fusion_file_id(outputpath)
        Net.download_qiagen_file(token, file_id, outputpath)
        file: str = Settings.COSMIC["FILE"]
        files = []

        try:
            files.append(".".join(file.split(".")[:-1]))

            with gzip.open(file, "rb") as archive, open(files[0], "wb") as out_file:
                shutil.copyfileobj(archive, out_file)

            db = CosmicDB(".")
            db.setup(files, delimiter="\t", skip_header=True)
        except Exception as ex:
            return_err.append(f'{Settings.COSMIC["NAME"]}: {ex}')

    @staticmethod
    def get_fusiongdb2(self, return_err: List[str], no_ssl) -> None:
        """Method for download FusionGDB2 database."""
        try:
            url: str = f'{Settings.FUSIONGDB2["HOSTNAME"]}/{Settings.FUSIONGDB2["FILE"]}'
            Net.get_large_file(url, no_ssl)
            file: str = f'{Settings.FUSIONGDB2["FILE"]}'
            df = pd.read_excel(file, engine="openpyxl")
            df["fusion"] = df["5'-gene (text format)"] + "--" + df["3'-gene (text format)"]
            file_csv = "fusionGDB2.csv"
            df["fusion"].to_csv(file_csv, header=False, index=False, sep=",", encoding="utf-8")

            db = FusionGDB2(".")
            db.setup([file_csv], delimiter=",", skip_header=False)

        except DownloadException as ex:
            return_err.append(f"FusionGDB2: {ex}")

    @staticmethod
    def get_mitelman(self, return_err: List[str], no_ssl) -> None:
        """Method for download Mitelman database."""
        try:
            url: str = f'{Settings.MITELMAN["HOSTNAME"]}/{Settings.MITELMAN["FILE"]}'
            Net.get_large_file(url, no_ssl)
            with ZipFile(Settings.MITELMAN["FILE"], "r") as archive:
                files = [
                    x for x in archive.namelist() if "MBCA.TXT.DATA" in x and not "MACOSX" in x
                ]
                archive.extractall()

            db = MitelmanDB(".")
            db.setup(files, delimiter="\t", skip_header=False, encoding="ISO-8859-1")
        except DownloadException as ex:
            return_err.append(f"Mitelman: {ex}")

    @staticmethod
    def clean():
        """Remove all files except *db and move to output dir."""
        for temp in glob.glob("*.db"):
            shutil.copy(temp, "../")
        os.chdir("../")
        shutil.rmtree("tmp_dir")

    @staticmethod
    def timestamp():
        """Create a timestamp file at DB creation"""
        timestr = time.strftime("%Y-%m-%d/%H:%M")
        text_file = open("DB-timestamp.txt", "w")
        text_file.write(timestr)
        text_file.close()
