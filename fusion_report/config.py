"""Configuration module"""
import base64
import os

from datetime import datetime
from typing import Any, Dict, List

from yaml import YAMLError, safe_load

from fusion_report.common.exceptions.config import ConfigException
from fusion_report.settings import Settings


class Config:
    """Class for adjusting report defined in configuration file."""

    def __init__(self) -> None:
        self._report_title = "nfcore/rnafusion summary report"
        self.logos = self._load_logos()
        self._institution: Dict[str, Any] = {}
        self._date: str = datetime.now().strftime(Settings.DATE_FORMAT)
        self._assets: Dict[str, List[str]] = {}

    @staticmethod
    def _load_logos() -> Dict[str, str]:
        logos = {}
        paths = {
            "main": "templates/assets/img/fusion-report.png",
            "rnafusion": "templates/assets/img/rnafusion_logo.png",
        }
        for key, path in paths.items():
            full_path = os.path.join(Settings.ROOT_DIR, path)
            with open(full_path, "rb") as image_file:
                logos[key] = base64.b64encode(image_file.read()).decode("utf-8")
        return logos

    @property
    def report_title(self) -> str:
        """Return title."""
        return self._report_title

    @report_title.setter
    def report_title(self, title: str) -> None:
        if title.strip():
            self._report_title = title.strip()

    @property
    def institution(self) -> Dict[str, Any]:
        """Return institution name, img and url."""
        return self._institution

    @institution.setter
    def institution(self, institution: Dict[str, str]) -> None:
        if "name" in institution.keys():
            self._institution["name"] = institution["name"]

        if "img" in institution.keys() and os.path.exists(institution["img"]):
            image = os.path.join(Settings.ROOT_DIR, institution["img"])
            self._institution["img"] = base64.b64encode(open(image, "rb").read()).decode("utf-8")

        if "url" in institution.keys():
            self._institution["url"] = institution["url"]

    @property
    def date(self) -> str:
        """Return date in format."""
        return self._date

    @date.setter
    def date(self, date_format: str) -> None:
        if date_format.strip():
            self._date = datetime.now().strftime(date_format)

    @property
    def assets(self) -> Dict[str, List[str]]:
        """Return HTML assets, custom CSS or Javascript."""
        return self._assets

    @assets.setter
    def assets(self, assets) -> None:
        for key, value in assets.items():
            if key in ("css", "js") and value is not None:
                self.assets[key] = [x for x in value if os.path.exists(x)]

    def parse(self, path) -> "Config":
        """
        Method for parsing the configuration file.

        Args:
            path (string): path to configuration file
        """
        if path:
            try:
                with open(path, "r", encoding="utf-8") as in_file:
                    try:
                        data = safe_load(in_file)
                        self.report_title = data["report_title"]
                        self.institution = data["institution"]
                        self.date = data["date_format"]
                        self.assets = data["assets"]
                        return self
                    except YAMLError as ex:
                        raise ConfigException(ex)
            except IOError as ex:
                raise ConfigException(ex)

        return self

    def json_serialize(self) -> Dict[str, Any]:
        """Helper serialization method for templating engine."""
        return {
            "report_title": self.report_title,
            "logos": self.logos,
            "institution": self.institution,
            "date": self.date,
            "assets": self.assets,
        }
