import os
import sys
from time import sleep
import rapidjson
from typing import Any, Dict, List
from fusion_report.helpers import progress_bar
from fusion_report.common.logger import Logger
from fusion_report.args_builder import ArgsBuilder
from fusion_report.common.fusion_manager import FusionManager
from fusion_report.common.report import Report
from fusion_report.download import Download
from fusion_report.data.fusiongdb import FusionGDB
from fusion_report.data.mitelman import MitelmanDB
from fusion_report.data.cosmic import CosmicDB
from fusion_report.common.exceptions.app import AppException
from fusion_report.common.exceptions.db import DbException
from fusion_report.common.exceptions.download import DownloadException

__version__ = 1.2


class App:

    def __init__(self):
        self.log = Logger().get_logger()
        try:
            cwd = os.path.dirname(os.path.abspath(__file__))
            settings_config = os.path.join(cwd, 'settings.json')
            self.settings = rapidjson.loads(open(settings_config, 'r').read())
            self.settings['weight']: float = float(100 / len(self.settings['args']['run']['tools']))
            self.settings['version']: float = __version__
            self.manager = FusionManager(self.settings)
            self.args = ArgsBuilder(self.settings)
        except IOError as ex:
            self.log.exception(ex.args[0])
            sys.exit(ex.args[0])

    def run(self):
        params = self.args.parse()
        try:
            if params.command == 'run':
                self.__preprocess(vars(params))
                self.__generate_report(vars(params))
                # export results
                # generate multiqc module
                # generate fusion list
            elif params.command == 'download':
                Download(params)
            else:
                sys.exit(f'Command {params.command} not recognized!')
        except (AppException, DbException, DownloadException) as ex:
            self.log.exception(ex)
            sys.exit(ex.args[0])

    def __preprocess(self, params) -> None:
        self.__parse_fusion_outputs(params)
        self.__enrich(params['db_path'])
        self.__score(params)

    def __generate_report(self, params) -> None:
        report = Report(params['config'], params['output'])
        fusions = self.manager.get_fusions()
        progress_bar(0, len(fusions))

        index_page = report.create_page(title='Summary', filename='index.html', page_variables={'sample': params['sample']})
        index_page.add_module('index_summary', self.manager, params={'tool_cutoff': params['tool_cutoff']})
        report.render(index_page)

        for i, fusion in enumerate(fusions):
            fusion_page = report.create_page(title=fusion.get_name(), page_variables={'sample': params['sample']})
            fusion_page.add_module('fusion_summary', params={'fusion': fusion})
            fusion_page.add_module('variations', params={'fusion': fusion.get_name(), 'db_path': params['db_path']})
            fusion_page.add_module('transcripts', params={'fusion': fusion.get_name(), 'db_path': params['db_path']})
            fusion_page.add_module('ppi', params={'fusion': fusion.get_name(), 'db_path': params['db_path']})
            fusion_page.add_module('drugs', params={'fusion': fusion.get_name(), 'db_path': params['db_path']})
            fusion_page.add_module('diseases', params={'fusion': fusion.get_name(), 'db_path': params['db_path']})
            report.render(fusion_page)

            # progress bar
            sleep(0.1)
            progress_bar(i, len(fusions))
            break

    def __parse_fusion_outputs(self, params: Dict[str, any]) -> None:
        for param, value in params.items():
            if param in self.manager.get_supported_tools() and value:
                # param: fusion tool
                self.manager.parse(param, value)

    def __enrich(self, path) -> None:
        local_fusions: Dict[str, List[str]] = {
            FusionGDB(path).name: FusionGDB(path).get_all_fusions(),
            MitelmanDB(path).name: MitelmanDB(path).get_all_fusions(),
            CosmicDB(path).name: CosmicDB(path).get_all_fusions()
        }
        for fusion in self.manager.get_fusions():
            for db_name, db_list in local_fusions.items():
                if fusion.get_name() in db_list:
                    fusion.add_db(db_name)

    def __score(self, params: Dict[str, Any]) -> None:
        """Custom scoring function for individual fusion.
        More information about the scoring function can be found in the documentation
        at https://github.com/matq007/fusion-report/docs/scoring-fusion
        Args:
            fusion_detail (FusionDetail)
            params (ArgumentParser)
        Returns:
            float: Estimate score of how genuine is the fusion.
        """

        for fusion in self.manager.get_fusions():
            score_explained: str = ''

            # tool estimation
            tool_score = 0.0
            tmp_explained = []
            for tool, _ in fusion.get_tools().items():
                tool_score += params[f'{tool.lower()}_weight'] / 100.0
                tmp_explained.append(format((params[f'{tool}_weight'] / 100.0), '.3f'))
            score_explained = f'0.5 * ({" + ".join(tmp_explained)})'

            # database estimation
            db_score = 0.0
            tmp_explained = []
            weights = {'fusiongdb': 0.20, 'cosmic': 0.40, 'mitelman': 0.40}
            for db_name in fusion.get_databases():
                db_score += 1.0 * weights[db_name.lower()]
                tmp_explained.append(format(weights[db_name.lower()], '.3f'))
            score_explained += f' + 0.5 * ({" + ".join(tmp_explained)})'

            score = float('%0.3f' % (0.5 * tool_score + 0.5 * db_score))
            fusion.set_score(score, score_explained)
