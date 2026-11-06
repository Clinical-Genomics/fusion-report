import base64
import glob
import gzip
import json
import os
import shutil
import subprocess
import tarfile
import time
from argparse import Namespace
from typing import List

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from fusion_report.common import db_builders
from fusion_report.common.exceptions.download import DownloadException
from fusion_report.common.fetch import download_file, download_source
from fusion_report.common.logger import Logger
from fusion_report.data.sources import get_source
from fusion_report.settings import Settings

LOG = Logger(__name__)

# Sanger's scripted-download API intermittently answers with 5xx; retry those a few times.
COSMIC_RETRY_STATUSES = (500, 502, 503, 504)
COSMIC_RETRY_TOTAL = 3
COSMIC_RETRY_BACKOFF = 2
COSMIC_TIMEOUT = 60


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
            " -o {output_path}{cosmic_file}"
        )
        cmd = file_request.format(
            token=token,
            file_id=file_id,
            output_path=output_path,
            cosmic_file=Settings.COSMIC["FILE"],
        )
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
            '-d "grant_type=password&client_id=603912630-14192122372034111918-SmRwso&username={uid}&password={pwd}" '  # noqa: E501
            '"https://apps.ingenuity.com/qiaoauth/oauth/token"'
        )
        cmd = token_request.format(uid=params.cosmic_usr, pwd=params.cosmic_passwd)
        token_response = Net.run_qiagen_cmd(cmd, True, True).decode("UTF-8")
        return json.loads(token_response)["access_token"]

    @staticmethod
    def get_large_file(url: str, no_ssl, fmt: str = "binary", source: str = "") -> str:
        """Download a file into the current directory and validate it (see `common.fetch`).

        Raises:
            DownloadException: on HTTP errors, HTML instead of data or a wrong/truncated file
        """
        file = url.split("/")[-1].split("?")[0]
        return download_file(url, file, fmt=fmt, no_ssl=no_ssl, source=source)

    @staticmethod
    def get_cosmic_from_sanger_url(token: str, file_path: str, no_ssl: bool = False) -> str:
        """Request a (pre-signed) download URL for a COSMIC file from the Sanger scripted API.

        Transient server errors (5xx) are retried with exponential backoff before giving up.
        """
        params = {"path": file_path, "bucket": "downloads"}
        url = Settings.COSMIC["HOSTNAME"]
        headers = {"Authorization": f"Basic {token}"}
        retry = Retry(
            total=COSMIC_RETRY_TOTAL,
            backoff_factor=COSMIC_RETRY_BACKOFF,
            status_forcelist=COSMIC_RETRY_STATUSES,
            allowed_methods=frozenset(["GET"]),
            raise_on_status=False,
        )
        with requests.Session() as session:
            session.mount("https://", HTTPAdapter(max_retries=retry))
            response = session.get(
                url, headers=headers, params=params, verify=not no_ssl, timeout=COSMIC_TIMEOUT
            )
        response.raise_for_status()
        return response.json().get("url")

    @staticmethod
    def describe_cosmic_error(err: requests.exceptions.RequestException, file_path: str) -> str:
        """Turn a failed COSMIC (Sanger) request into an actionable error message."""
        status = getattr(getattr(err, "response", None), "status_code", None)
        if status in (401, 403):
            hint = (
                "authentication failed. Check --cosmic_usr (the e-mail address of your COSMIC "
                "account) and --cosmic_passwd, and that you can log in at "
                "https://cancer.sanger.ac.uk/cosmic/login."
            )
        elif status == 400:
            hint = (
                "the request was rejected as malformed. If you used --cosmic_token, it must be "
                "base64('<email>:<password>'); otherwise use --cosmic_usr/--cosmic_passwd."
            )
        elif status == 404:
            hint = (
                f"the file '{file_path}' was not found. COSMIC {Settings.COSMIC['VERSION']} "
                "may no longer be available for scripted download."
            )
        elif status is not None and status >= 500:
            hint = (
                f"the Sanger server returned HTTP {status} for '{file_path}' (after "
                f"{COSMIC_RETRY_TOTAL} retries). This is a server-side error and is often "
                "temporary, so try again later. If it persists, log in at "
                "https://cancer.sanger.ac.uk/cosmic and check that your account is active, that "
                "you have accepted the current non-commercial licence, and that you can download "
                f"'{Settings.COSMIC['TARFILE']}' in the browser. Commercial users must download "
                "COSMIC via QIAGEN (--qiagen). Use --no-cosmic to skip COSMIC."
            )
        elif isinstance(err, requests.exceptions.SSLError):
            hint = (
                "SSL certificate verification failed. If you are behind a proxy that intercepts "
                "TLS, re-run with -no_ssl."
            )
        elif isinstance(err, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
            hint = (
                "could not reach https://cancer.sanger.ac.uk. Check your network/proxy settings "
                "or try again later."
            )
        else:
            hint = "the download request failed."
        return f'{Settings.COSMIC["NAME"]}: {hint} (details: {err})'

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
                target_file = Settings.COSMIC["FILE"]
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
        file_path = f"grch38/cosmic/{Settings.COSMIC['VERSION']}/{Settings.COSMIC['TARFILE']}"
        try:
            download_url = Net.get_cosmic_from_sanger_url(token, file_path=file_path, no_ssl=no_ssl)

            if not download_url:
                raise ValueError("Failed to retrieve the download URL.")

            LOG.info(f"Download URL: {download_url}")
            Net.get_large_file(download_url, no_ssl, fmt="tar", source=Settings.COSMIC["NAME"])
            if Net.extract_tar(Settings.COSMIC["TARFILE"], ".") is None:
                raise ValueError(f"{Settings.COSMIC['FILE']} not found in the downloaded archive")
            db_builders.build_cosmic(Settings.COSMIC["FILE"])

        except requests.exceptions.RequestException as req_err:
            return_err.append(Net.describe_cosmic_error(req_err, file_path))
        except DownloadException as ex:
            return_err.append(str(ex))
        except Exception as ex:
            return_err.append(f'{Settings.COSMIC["NAME"]}: {ex}')

    @staticmethod
    def get_cosmic_from_qiagen(token: str, return_err: List[str], outputpath: str, no_ssl) -> None:
        """Method for download COSMIC database from QIAGEN."""
        try:
            Net.get_qiagen_files(token, outputpath)
        except Exception as ex:
            LOG.info(ex)

        file_id = Net.fetch_fusion_file_id(outputpath)
        Net.download_qiagen_file(token, file_id, outputpath)
        try:
            db_builders.build_cosmic(Settings.COSMIC["FILE"])
        except Exception as ex:
            return_err.append(f'{Settings.COSMIC["NAME"]}: {ex}')

    @staticmethod
    def get_fusiongdb2(self, return_err: List[str], no_ssl) -> None:
        """Download FusionGDB2 (trying all configured URLs) and build fusiongdb2.db."""
        source = get_source("fusiongdb2")
        try:
            download_source(source, source.filename, no_ssl=no_ssl)
            db_builders.build_fusiongdb2(source.filename)
        except DownloadException as ex:
            return_err.append(str(ex))
        except Exception as ex:
            return_err.append(f"{source.name}: {ex}")

    @staticmethod
    def get_mitelman(self, return_err: List[str], no_ssl) -> None:
        """Download Mitelman (trying all configured URLs) and build mitelman.db."""
        source = get_source("mitelman")
        try:
            download_source(source, source.filename, no_ssl=no_ssl)
            db_builders.build_mitelman(source.filename)
        except DownloadException as ex:
            return_err.append(str(ex))
        except Exception as ex:
            return_err.append(f"{source.name}: {ex}")

    @staticmethod
    def clean(tmp_dir: str, output_dir: str):
        """Move generated databases to output and remove temporary download directory."""
        for temp in glob.glob(os.path.join(tmp_dir, "*.db")):
            shutil.copy(temp, output_dir)
        shutil.rmtree(tmp_dir, ignore_errors=True)

    @staticmethod
    def timestamp(output_dir: str = "."):
        """Create a timestamp file at DB creation"""
        timestr = time.strftime("%Y-%m-%d/%H:%M")
        text_file = open(os.path.join(output_dir, "DB-timestamp.txt"), "w")
        text_file.write(timestr)
        text_file.close()
