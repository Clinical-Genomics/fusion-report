"""Unit tests for fusion_report.download (network calls mocked)."""

import os
from argparse import Namespace
from unittest import mock

import pytest

from fusion_report.common.exceptions.download import DownloadException
from fusion_report.download import Download


def _params(output, **overrides):
    values = dict(
        output=str(output),
        no_mitelman=True,
        no_fusiongdb2=True,
        no_cosmic=False,
        no_ssl=False,
        qiagen=False,
        cosmic_token=None,
        cosmic_usr="me@example.org",
        cosmic_passwd="secret",
    )
    values.update(overrides)
    return Namespace(**values)


@pytest.fixture(autouse=True)
def _restore_cwd():
    cwd = os.getcwd()
    yield
    os.chdir(cwd)


def test_download_reports_cosmic_errors_readably(tmp_path):
    def fail(token, return_err, no_ssl, output):
        return_err.append("COSMIC: first problem")
        return_err.append("Mitelman: second problem")

    with mock.patch("fusion_report.download.Net.get_cosmic_from_sanger", side_effect=fail):
        with pytest.raises(DownloadException) as excinfo:
            Download(_params(tmp_path))

    assert str(excinfo.value) == "COSMIC: first problem\nMitelman: second problem"


def test_download_qiagen_calls_with_matching_signature(tmp_path):
    with (
        mock.patch("fusion_report.download.Net.get_cosmic_qiagen_token", return_value="T"),
        mock.patch("fusion_report.download.Net.get_cosmic_from_qiagen") as qiagen,
        mock.patch("fusion_report.download.Net.clean"),
        mock.patch("fusion_report.download.Net.timestamp"),
    ):
        Download(_params(tmp_path, qiagen=True))

    qiagen.assert_called_once()
    assert qiagen.call_args.args == ("T", [], str(tmp_path))
