import argparse
import rapidjson
import os
import sys
from typing import Any, Dict, List
from fusion_report.logger import Logger
from fusion_report.args_builder import ArgsBuilder
from fusion_report.common.download import Download
from fusion_report.common.fusion_manager import FusionManager
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
                self.__preprocess(vars(params))
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

    def __preprocess(self, params: Dict[str, any]) -> None:
        supported_tools: List[str] = [
            tool['key'].replace('--', '') for tool in self.settings['args']['run']['tools']
        ]
        manager = FusionManager(supported_tools)
        for param, value in params.items():
            if param in supported_tools and value is not None:
                # param: fusion tool
                manager.parse(param, value)
        manager.print()
