import argparse
import rapidjson
import os
import sys
from typing import Dict, Any
from fusion_report.logger import Logger
from fusion_report.args_builder import ArgsBuilder
from fusion_report.common.download import Download
from fusion_report.common.exceptions.download import DownloadException

__version__ = 1.2

class App:

    def __init__(self):
        self.log = Logger().get_logger()
        try:
            cwd = os.path.dirname(os.path.abspath(__file__))
            settings_config = os.path.join(cwd, 'settings.json')
            self.settings = rapidjson.loads(open(settings_config, 'r').read())
        except IOError as ex:
            self.log.exception(ex.args[0])
            sys.exit(ex.args[0])

        self.settings['weight']: float = float(100/len(self.settings['args']['run']['tools']))
        self.settings['version']: float = __version__
        self.args = ArgsBuilder(self.settings)

    def run(self):
        params = self.args.parse()
        if params.command == 'run':
            try:
                print('Hi')
            except Exception as ex:
                self.log.exception(ex)
        elif params.command == 'download':
            try:
                Download(params)
            except DownloadException as ex:
                self.log.exception(ex.args[0])
                sys.exit(ex.args[0])
        else:
            sys.exit(f'Command {params.command} not recognized!')
