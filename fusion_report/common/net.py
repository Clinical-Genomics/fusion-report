import base64
import glob
import gzip
import io
import os
import shutil
import tarfile
import time
from argparse import Namespace
from typing import List
from urllib.parse import urlencode

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from fusion_report.common import db_builders
from fusion_report.common.exceptions.download import DownloadException
from fusion_report.common.fetch import TIMEOUT, download_file, make_session
from fusion_report.common.logger import Logger
from fusion_report.settings import Settings

LOG = Logger(__name__)

# Sanger's scripted-download API intermittently answers with 5xx; retry those a few times.
COSMIC_RETRY_STATUSES = (500, 502, 503, 504)
COSMIC_RETRY_TOTAL = 3
COSMIC_RETRY_BACKOFF = 2
COSMIC_TIMEOUT = 60

QIAGEN_CLIENT_ID = "603912630-14192122372034111918-SmRwso"
QIAGEN_TOKEN_URL = "https://apps.ingenuity.com/qiaoauth/oauth/token"
QIAGEN_FILES_URL = "https://my.qiagendigitalinsights.com/bbp/data/files/cosmic"
QIAGEN_DOWNLOAD_URL = "https://my.qiagendigitalinsights.com/bbp/data/download/cosmic-download"


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
    def get_cosmic_qiagen_token(params: Namespace) -> str:
        """Request a QIAGEN access token (OAuth password grant).

        Credentials are sent in the request body, never on a command line.
        """
        if not params.cosmic_usr or not params.cosmic_passwd:
            raise DownloadException(
                "QIAGEN: --cosmic_usr and --cosmic_passwd (your QIAGEN login) are required "
                "with --qiagen"
            )
        data = {
            "grant_type": "password",
            "client_id": QIAGEN_CLIENT_ID,
            "username": params.cosmic_usr,
            "password": params.cosmic_passwd,
        }
        try:
            with make_session(getattr(params, "no_ssl", False)) as session:
                response = session.post(QIAGEN_TOKEN_URL, data=data, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()["access_token"]
        except requests.exceptions.HTTPError as ex:
            status = ex.response.status_code if ex.response is not None else "?"
            hint = (
                " Check your QIAGEN username and password."
                if status in (400, 401, 403)
                else " The QIAGEN server may be unavailable, try again later."
            )
            raise DownloadException(f"QIAGEN: login failed (HTTP {status}).{hint}") from ex
        except (requests.exceptions.RequestException, ValueError, KeyError) as ex:
            raise DownloadException(f"QIAGEN: could not get an access token: {ex}") from ex

    @staticmethod
    def get_qiagen_files(token: str, session: requests.Session) -> str:
        """Return the QIAGEN COSMIC file listing (TSV: file_id, file_name, genome_draft)."""
        response = session.get(
            QIAGEN_FILES_URL, headers={"Authorization": f"Bearer {token}"}, timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.text

    @staticmethod
    def fetch_fusion_file_id(files_tsv: str) -> str:
        """Find the file id of the COSMIC fusion file (GRCh38) in the QIAGEN file listing."""
        df = pd.read_csv(
            io.StringIO(files_tsv),
            names=["file_id", "file_name", "genome_draft"],
            sep="\t",
        )
        matches = df.loc[
            (df["file_name"] == Settings.COSMIC["FILE"]) & (df["genome_draft"] == "cosmic/GRCh38"),
            "file_id",
        ]
        if matches.empty:
            raise ValueError(
                f"{Settings.COSMIC['FILE']} (GRCh38) is not available from QIAGEN. Check "
                "--cosmic-version."
            )
        return str(matches.values[0])

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
        """Download the COSMIC fusion file from QIAGEN (commercial licence) and build cosmic.db
        in the current directory."""
        try:
            with make_session(no_ssl) as session:
                file_id = Net.fetch_fusion_file_id(Net.get_qiagen_files(token, session))
                session.headers["Authorization"] = f"Bearer {token}"
                download_file(
                    f"{QIAGEN_DOWNLOAD_URL}?{urlencode({'name': file_id})}",
                    Settings.COSMIC["FILE"],
                    fmt="gzip",
                    session=session,
                    source=Settings.COSMIC["NAME"],
                )
            db_builders.build_cosmic(Settings.COSMIC["FILE"])
        except DownloadException as ex:
            return_err.append(str(ex))
        except requests.exceptions.RequestException as ex:
            return_err.append(f'{Settings.COSMIC["NAME"]}: QIAGEN request failed: {ex}')
        except Exception as ex:
            return_err.append(f'{Settings.COSMIC["NAME"]}: {ex}')

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
