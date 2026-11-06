"""Unit tests for COSMIC (Sanger) download handling in fusion_report.common.net."""

from argparse import Namespace
from unittest import mock

import pytest
import requests

from fusion_report.common.exceptions.download import DownloadException
from fusion_report.common.net import COSMIC_RETRY_STATUSES, COSMIC_RETRY_TOTAL, Net
from fusion_report.settings import Settings

FILE_PATH = f"grch38/cosmic/{Settings.COSMIC['VERSION']}/{Settings.COSMIC['TARFILE']}"


def _http_error(status: int) -> requests.exceptions.HTTPError:
    response = requests.Response()
    response.status_code = status
    response.url = Settings.COSMIC["HOSTNAME"]
    response.reason = "Error"
    return requests.exceptions.HTTPError(f"{status} Error", response=response)


def _mock_session(response):
    session = mock.MagicMock()
    session.__enter__.return_value = session
    session.get.return_value = response
    return session


def test_get_cosmic_token_from_user_and_password():
    params = Namespace(cosmic_token=None, cosmic_usr="me@example.org", cosmic_passwd="secret")
    # base64("me@example.org:secret"), no trailing newline
    assert Net.get_cosmic_token(params) == "bWVAZXhhbXBsZS5vcmc6c2VjcmV0"


def test_get_cosmic_token_prefers_explicit_token():
    params = Namespace(cosmic_token="abc", cosmic_usr="u", cosmic_passwd="p")
    assert Net.get_cosmic_token(params) == "abc"


def test_get_cosmic_token_missing_credentials():
    params = Namespace(cosmic_token=None, cosmic_usr="u", cosmic_passwd=None)
    with pytest.raises(DownloadException):
        Net.get_cosmic_token(params)


def test_get_cosmic_from_sanger_url_request_and_retry_config():
    response = mock.MagicMock()
    response.json.return_value = {"url": "https://signed.example/file.tar"}
    session = _mock_session(response)

    with mock.patch("fusion_report.common.net.requests.Session", return_value=session):
        url = Net.get_cosmic_from_sanger_url("TOKEN", FILE_PATH)

    assert url == "https://signed.example/file.tar"
    _, kwargs = session.get.call_args
    assert session.get.call_args.args[0] == Settings.COSMIC["HOSTNAME"]
    assert kwargs["params"] == {"path": FILE_PATH, "bucket": "downloads"}
    assert kwargs["headers"] == {"Authorization": "Basic TOKEN"}
    assert kwargs["verify"] is True
    assert kwargs["timeout"] > 0
    response.raise_for_status.assert_called_once()

    adapter = session.mount.call_args.args[1]
    retry = adapter.max_retries
    assert retry.total == COSMIC_RETRY_TOTAL
    assert set(COSMIC_RETRY_STATUSES) <= set(retry.status_forcelist)
    assert 500 in retry.status_forcelist


def test_get_cosmic_from_sanger_url_no_ssl_disables_verification():
    response = mock.MagicMock()
    response.json.return_value = {"url": "x"}
    session = _mock_session(response)
    with mock.patch("fusion_report.common.net.requests.Session", return_value=session):
        Net.get_cosmic_from_sanger_url("TOKEN", FILE_PATH, no_ssl=True)
    assert session.get.call_args.kwargs["verify"] is False


def test_get_cosmic_from_sanger_url_raises_http_error():
    response = mock.MagicMock()
    response.raise_for_status.side_effect = _http_error(500)
    session = _mock_session(response)
    with mock.patch("fusion_report.common.net.requests.Session", return_value=session):
        with pytest.raises(requests.exceptions.HTTPError):
            Net.get_cosmic_from_sanger_url("TOKEN", FILE_PATH)


@pytest.mark.parametrize(
    "status, expected",
    [
        (401, "authentication failed"),
        (403, "authentication failed"),
        (400, "malformed"),
        (404, "not found"),
        (500, "server-side error"),
        (503, "server-side error"),
    ],
)
def test_describe_cosmic_error_http(status, expected):
    msg = Net.describe_cosmic_error(_http_error(status), FILE_PATH)
    assert msg.startswith("COSMIC: ")
    assert expected in msg
    assert f"{status} Error" in msg


def test_describe_cosmic_error_500_is_actionable():
    msg = Net.describe_cosmic_error(_http_error(500), FILE_PATH)
    assert FILE_PATH in msg
    assert "--qiagen" in msg
    assert "--no-cosmic" in msg
    assert "try again later" in msg


def test_describe_cosmic_error_connection_and_ssl():
    msg = Net.describe_cosmic_error(requests.exceptions.ConnectionError("boom"), FILE_PATH)
    assert "could not reach" in msg
    msg = Net.describe_cosmic_error(requests.exceptions.SSLError("bad cert"), FILE_PATH)
    assert "-no_ssl" in msg


def test_get_cosmic_from_sanger_collects_actionable_error():
    errors = []
    with mock.patch.object(Net, "get_cosmic_from_sanger_url", side_effect=_http_error(500)):
        Net.get_cosmic_from_sanger("TOKEN", errors, False, ".")
    assert len(errors) == 1
    assert "server-side error" in errors[0]
    assert FILE_PATH in errors[0]


def test_get_large_file_verifies_ssl_by_default(tmp_path, monkeypatch):
    from fusion_report.common.fetch import make_session

    assert make_session().verify is True
    assert make_session(no_ssl=True).verify is False

    monkeypatch.chdir(tmp_path)
    with mock.patch("fusion_report.common.net.download_file") as download:
        Net.get_large_file("https://example.org/file.zip?sig=1", True, fmt="zip")
    download.assert_called_once_with(
        "https://example.org/file.zip?sig=1", "file.zip", fmt="zip", no_ssl=True, source=""
    )
