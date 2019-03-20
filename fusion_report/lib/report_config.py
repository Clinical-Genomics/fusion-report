"""Module for Report Configuration"""
import os
import base64
from datetime import datetime
from yaml import safe_load, YAMLError

class ReportConfig:
    """Class for adjusting report"""
    def __init__(self, config=None):
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.report_title = 'nfcore/rnafusion summary report'
        self.logos = {
            'main': base64.b64encode(open(
                os.path.join(self.current_path, '../../docs/_src/_static/fusion-report.png'), 'rb'
            ).read()).decode('utf-8'),
            'rnafusion': base64.b64encode(open(
                os.path.join(self.current_path, '../templates/assets/img/rnafusion_logo.png'), 'rb'
            ).read()).decode('utf-8')
        }
        self.institution = {}
        self.date_format = '%d/%m/%Y'
        self.date = datetime.now().strftime(self.date_format)
        self.assets = {}

        if config is not None:
            self.__parse(config)

    def get_variables(self):
        """Helper method returning all variables. Used for Jinja templating."""
        return self.__dict__

    def __parse(self, config):
        """
        Method for parsing the configuration file.

        Args:
            config (string): path to configuration file
        """
        try:
            with open(config, 'r', encoding='utf-8') as in_file:
                try:
                    data = safe_load(in_file)
                    self.__set_title(data)
                    self.__set_institution(data)
                    self.__set_date_format(data)
                    self.__set_assets(data)
                except YAMLError as error:
                    print(error)
        except IOError as error:
            print(error)
            print('Configuration file not found, skipping ...')

    def __set_title(self, config):
        """Helper function for setting a custom title."""
        if config['report_title'] is not None:
            self.report_title = config['report_title'].strip()

    def __set_institution(self, config):
        """Helper function for adding an institution."""
        if config['institution'] is not None:
            if 'name' in config['institution']:
                self.institution['name'] = config['institution']['name']

            if 'img' in config['institution'] and os.path.exists(config['institution']['img']):
                self.institution['img'] = base64.b64encode(
                    open(os.path.join(self.current_path, config['institution']['img']), 'rb').read()
                ).decode('utf-8')

            if 'url' in config['institution']:
                self.institution['url'] = config['institution']['url']

    def __set_date_format(self, config):
        """Helper function for setting a custom date format."""
        if config['date_format'] is not None:
            self.date_format = config['date_format']
            self.date = datetime.now().strftime(self.date_format)

    def __set_assets(self, config):
        """Helper function for adding custom CSS or Javascript."""
        if config['assets'] is not None:
            for key, value in config['assets'].items():
                if key in ('css', 'js') and value is not None:
                    self.assets[key] = [x for x in value if os.path.exists(x)]
