"""Tests for --cosmic-version and the QIAGEN (commercial) COSMIC download."""

import gzip
import json
from argparse import Namespace
from unittest import mock
from urllib.parse import parse_qs

import pytest

from fusion_report.common import net
from fusion_report.common.db_builders import cosmic_columns
from fusion_report.common.exceptions.download import DownloadException
from fusion_report.common.net import Net
from fusion_report.data.cosmic import CosmicDB
from fusion_report.download import Download
from fusion_report.settings import Settings


def _cosmic_tsv(*pairs) -> bytes:
    columns = cosmic_columns()
    lines = ["\t".join(columns)]
    for index, (five, three) in enumerate(pairs, start=1):
        row = {name: "" for name in columns}
        row.update(COSMIC_SAMPLE_ID=str(index), FIVE_PRIME_GENE_SYMBOL=five)
        row.update(THREE_PRIME_GENE_SYMBOL=three)
        lines.append("\t".join(row[name] for name in columns))
    return ("\n".join(lines) + "\n").encode()


def _params(output, **overrides):
    values = dict(
        output=str(output),
        no_mitelman=True,
        no_fusiongdb2=True,
        no_cosmic=False,
        no_ssl=False,
        qiagen=True,
        cosmic_token=None,
        cosmic_usr="me@example.org",
        cosmic_passwd="p'a\"ss; rm -rf /",
        cosmic_version="v101",
    )
    values.update(overrides)
    return Namespace(**values)


# --- --cosmic-version -----------------------------------------------------------------------


def test_use_cosmic_version_updates_file_names():
    Settings.use_cosmic_version("v103")
    assert Settings.COSMIC["VERSION"] == "v103"
    assert Settings.COSMIC["TARFILE"] == "Cosmic_Fusion_Tsv_v103_GRCh38.tar"
    assert Settings.COSMIC["FILE"] == "Cosmic_Fusion_v103_GRCh38.tsv.gz"


@pytest.mark.parametrize("version", ["101", "v10a", "", "../v101"])
def test_use_cosmic_version_rejects_invalid(version):
    with pytest.raises(ValueError, match="invalid COSMIC version"):
        Settings.use_cosmic_version(version)


def test_download_rejects_invalid_version(tmp_path):
    with pytest.raises(DownloadException, match="COSMIC: invalid COSMIC version"):
        Download(_params(tmp_path, qiagen=False, cosmic_version="latest"))


def test_sanger_download_requests_selected_version(tmp_path):
    with mock.patch.object(Net, "get_cosmic_from_sanger_url", return_value=None) as url:
        with pytest.raises(DownloadException):
            Download(_params(tmp_path, qiagen=False, cosmic_version="v103"))
    assert url.call_args.kwargs["file_path"] == (
        "grch38/cosmic/v103/Cosmic_Fusion_Tsv_v103_GRCh38.tar"
    )


# --- QIAGEN ---------------------------------------------------------------------------------


@pytest.fixture
def qiagen(http_server, monkeypatch):
    """A fake QIAGEN: token endpoint, file listing and download."""
    monkeypatch.setattr(net, "QIAGEN_TOKEN_URL", http_server.url("/token"))
    monkeypatch.setattr(net, "QIAGEN_FILES_URL", http_server.url("/files"))
    monkeypatch.setattr(net, "QIAGEN_DOWNLOAD_URL", http_server.url("/download"))
    http_server.add("/token", (200, {"Content-Type": "application/json"}, b'{"access_token": "T"}'))
    listing = (
        "id-other\tCosmic_Other.tsv.gz\tcosmic/GRCh38\n"
        f"id-fusion\t{Settings.COSMIC['FILE']}\tcosmic/GRCh38\n"
        f"id-37\t{Settings.COSMIC['FILE']}\tcosmic/GRCh37\n"
    )
    http_server.add(
        "/files", (200, {"Content-Type": "text/tab-separated-values"}, listing.encode())
    )
    http_server.add(
        "/download",
        (200, {"Content-Type": "application/gzip"}, gzip.compress(_cosmic_tsv(("BCR", "ABL1")))),
    )
    return http_server


def test_qiagen_token_is_requested_without_shell(qiagen):
    assert not hasattr(Net, "run_qiagen_cmd")
    params = _params("db")
    assert Net.get_cosmic_qiagen_token(params) == "T"
    # credentials (incl. shell metacharacters) are form-encoded in the POST body
    body = parse_qs(qiagen.request_bodies[-1].decode())
    assert body["password"] == ["p'a\"ss; rm -rf /"]
    assert body["username"] == ["me@example.org"] and body["grant_type"] == ["password"]


@pytest.mark.parametrize("status, hint", [(401, "username and password"), (503, "unavailable")])
def test_qiagen_token_errors(qiagen, status, hint):
    qiagen.add("/token", (status, {"Content-Type": "application/json"}, b"{}"))
    with pytest.raises(
        DownloadException, match=f"QIAGEN: login failed \\(HTTP {status}\\).*{hint}"
    ):
        Net.get_cosmic_qiagen_token(_params("db"))


def test_qiagen_token_requires_credentials():
    with pytest.raises(DownloadException, match="--cosmic_usr and --cosmic_passwd"):
        Net.get_cosmic_qiagen_token(_params("db", cosmic_passwd=None))


def test_fetch_fusion_file_id_picks_grch38_fusion_file():
    listing = f"a\tother\tcosmic/GRCh38\nb\t{Settings.COSMIC['FILE']}\tcosmic/GRCh38\n"
    assert Net.fetch_fusion_file_id(listing) == "b"
    with pytest.raises(ValueError, match="not available from QIAGEN"):
        Net.fetch_fusion_file_id("a\tother\tcosmic/GRCh38\n")


def test_download_with_qiagen_end_to_end(qiagen, tmp_path):
    Download(_params(tmp_path))

    assert "BCR--ABL1" in CosmicDB(str(tmp_path)).get_all_fusions()
    assert qiagen.hits["/download"] == 1
    # the bearer token is sent to the listing and the download
    assert all(h.get("Authorization") == "Bearer T" for h in qiagen.request_headers[1:])
    manifest = json.loads((tmp_path / "db_manifest.json").read_text())
    assert manifest["sources"]["cosmic"]["origin"] == "qiagen"
    assert "p'a" not in json.dumps(manifest)


def test_qiagen_html_download_is_rejected(qiagen, tmp_path):
    qiagen.add("/download", (200, {"Content-Type": "text/html"}, b"<html>login</html>"))
    with pytest.raises(
        DownloadException, match="COSMIC: expected a gzip file but received an HTML"
    ):
        Download(_params(tmp_path))
    assert not (tmp_path / "cosmic.db").exists()


def test_qiagen_missing_file_mentions_version(qiagen, tmp_path):
    with pytest.raises(DownloadException, match="not available from QIAGEN.*--cosmic-version"):
        Download(_params(tmp_path, cosmic_version="v999"))
