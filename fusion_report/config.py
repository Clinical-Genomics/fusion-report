"""Configuration module"""
import base64
import os
from datetime import datetime
from typing import Any, Dict, List

from yaml import safe_load, YAMLError

from fusion_report.common.exceptions.config import ConfigException


class Config:
    """Class for adjusting report defined in configuration file.

    Attributes:
        __current_path: current working directory
        __report_title: Title of the report
        __logos: Dictionary of logos: fusion-report and nf-core/rnafusion
        __institution: Institution name
        __date: Date in format '%d/%m/%Y'
        __assets: Additional CSS and JS files
    """

    def __init__(self) -> None:
        self.__current_path: str = os.path.dirname(os.path.abspath(__file__))
        self.__report_title: str = 'nfcore/rnafusion summary report'
        self.__logos: Dict[str, str] = {
            'main': base64.b64encode(open(
                os.path.join(self.__current_path, '../docs/img/fusion-report.png'), 'rb'
            ).read()).decode('utf-8'),
            'rnafusion': base64.b64encode(open(
                os.path.join(self.__current_path, '../docs/img/rnafusion_logo.png'), 'rb'
            ).read()).decode('utf-8')
        }
        self.__institution: Dict[str, Any] = {}
        self.__date: str = datetime.now().strftime('%d/%m/%Y')
        self.__assets: Dict[str, List[str]] = {}

    def parse(self, path) -> Dict[str, Any]:
        """
        Method for parsing the configuration file.

        Args:
            path (string): path to configuration file
        """
        config: Dict[str, Any] = {
            'report_title': self.__report_title,
            'logos': self.__logos,
            'institution': self.__institution,
            'date': self.__date,
            'assets': self.__assets
        }

        if not path:
            # return default configuration
            return config

        try:
            with open(path, 'r', encoding='utf-8') as in_file:
                try:
                    data = safe_load(in_file)
                    self.__set_title(data)
                    self.__set_institution(data)
                    self.__set_date_format(data)
                    self.__set_assets(data)
                    return config
                except YAMLError as ex:
                    raise ConfigException(ex)
        except IOError as ex:
            raise ConfigException(ex)

    def __set_title(self, config: Dict[str, Any]) -> None:
        """Helper function for setting a custom title."""
        if config['report_title'] is not None:
            self.__report_title = config['report_title'].strip()

    def __set_institution(self, config: Dict[str, Any]) -> None:
        """Helper function for adding an institution."""
        if config['institution'] is not None:
            if 'name' in config['institution']:
                self.__institution['name'] = config['institution']['name']

            if 'img' in config['institution'] and os.path.exists(config['institution']['img']):
                image = os.path.join(self.__current_path, config['institution']['img'])
                self.__institution['img'] = base64.b64encode(
                    open(image, 'rb').read()
                ).decode('utf-8')

            if 'url' in config['institution']:
                self.__institution['url'] = config['institution']['url']

    def __set_date_format(self, config) -> None:
        """Helper function for setting a custom date format."""
        if config['date_format'] is not None:
            self.__date = datetime.now().strftime(config['date_format'])

    def __set_assets(self, config) -> None:
        """Helper function for adding custom CSS or Javascript."""
        if config['assets'] is not None:
            for key, value in config['assets'].items():
                if key in ('css', 'js') and value is not None:
                    self.__assets[key] = [x for x in value if os.path.exists(x)]
