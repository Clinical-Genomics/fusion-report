"""Main app module"""
import csv
import os
import sys
import time
from argparse import Namespace
from typing import Any, Dict, List

import rapidjson
from tqdm import tqdm

from fusion_report.args_builder import ArgsBuilder
from fusion_report.common.exceptions.app import AppException
from fusion_report.common.exceptions.db import DbException
from fusion_report.common.exceptions.download import DownloadException
from fusion_report.common.fusion_manager import FusionManager
from fusion_report.common.logger import Logger
from fusion_report.common.models.fusion import Fusion
from fusion_report.common.report import Report
from fusion_report.data.cosmic import CosmicDB
from fusion_report.data.fusiongdb import FusionGDB
from fusion_report.data.mitelman import MitelmanDB
from fusion_report.download import Download

__version__ = 2.0


class App:
    """The class implements core methods.

    Attributes:
        __manager: Fusion manager
        ___args: Parsed settings
    """

    def __init__(self) -> None:
        try:
            self.__args = ArgsBuilder(__version__)
            self.__manager = FusionManager(self.__args.get_supported_tools())
        except IOError as ex:
            raise AppException(ex)

    def build_args(self):
        """Builds command-line arguments."""
        self.__args.build()

    def run(self):
        """Parse parameters and execute commands.

        Raises:
            AppException
        """
        params = self.__args.parse()
        try:
            if params.command == 'run':
                self.__preprocess(params)
                self.__generate_report(params)
                self.__export_results(params.output, params.export)
                self.generate_multiqc(
                    params.output, self.__manager.get_fusions(),
                    params.sample, len(self.__manager.get_running_tools())
                )
                self.__generate_fusion_list(params.output, params.tool_cutoff)
            elif params.command == 'download':
                Download(params)
            else:
                sys.exit(f'Command {params.command} not recognized!')
        except (AppException, DbException, DownloadException, IOError) as ex:
            raise AppException(ex)

    def __preprocess(self, params: Namespace) -> None:
        """Parse, enrich and score fusion."""
        self.__parse_fusion_outputs(vars(params))
        self.__enrich(params.db_path)
        self.__score(vars(params))

    def __generate_report(self, params: Namespace) -> None:
        """Generate fusion report with all pages."""
        report = Report(params.config, params.output)
        fusions = self.__manager.get_fusions()

        index_page = report.create_page(
            'Summary', filename='index.html', page_variables={'sample': params.sample}
        )
        index_page.add_module(
            'index_summary', self.__manager, params={'tool_cutoff': params.tool_cutoff}
        )
        report.render(index_page)

        with tqdm(total=len(fusions)) as pbar:
            for fusion in fusions:
                fusion_page = report.create_page(
                    fusion.get_name(), page_variables={'sample': params.sample}
                )
                fusion_page.add_module('fusion_summary', params={'fusion': fusion})
                fusion_page.add_module(
                    'fusiongdb.variations',
                    params={'fusion': fusion.get_name(), 'db_path': params.db_path}
                )
                fusion_page.add_module(
                    'fusiongdb.transcripts',
                    params={'fusion': fusion.get_name(), 'db_path': params.db_path}
                )
                fusion_page.add_module(
                    'fusiongdb.ppi',
                    params={'fusion': fusion.get_name(), 'db_path': params.db_path}
                )
                fusion_page.add_module(
                    'fusiongdb.drugs',
                    params={'fusion': fusion.get_name(), 'db_path': params.db_path}
                )
                fusion_page.add_module(
                    'fusiongdb.diseases',
                    params={'fusion': fusion.get_name(), 'db_path': params.db_path}
                )
                report.render(fusion_page)
                pbar.set_description(f'Processing {fusion.get_name()}')
                time.sleep(0.1)
                pbar.update(1)

    def __parse_fusion_outputs(self, params: Dict[str, Any]) -> None:
        """Executes parsing for each provided fusion detection tool."""
        for param, value in params.items():
            if param in self.__manager.get_supported_tools() and value:
                # param: fusion tool
                # value: fusion tool output
                self.__manager.parse(param, value)

    def __enrich(self, path: str) -> None:
        """Enrich fusion with all relevant information from local databases."""
        local_fusions: Dict[str, List[str]] = {
            FusionGDB(path).get_name(): FusionGDB(path).get_all_fusions(),
            MitelmanDB(path).get_name(): MitelmanDB(path).get_all_fusions(),
            CosmicDB(path).get_name(): CosmicDB(path).get_all_fusions()
        }
        for fusion in self.__manager.get_fusions():
            for db_name, db_list in local_fusions.items():
                if fusion.get_name() in db_list:
                    fusion.add_db(db_name)

    def __export_results(self, path: str, extension: str) -> None:
        """Export results.
        Currently supporting file types: JSON and CSV
        """
        results = []
        dest = f"{os.path.join(path, 'fusions')}.{extension}"
        if extension == 'json':
            with open(dest, 'w', encoding='utf-8') as output:
                for fusion in self.__manager.get_fusions():
                    results.append(fusion.json_serialize())
                output.write(rapidjson.dumps(results))
        elif extension == 'csv':
            with open(dest, "w", encoding='utf-8') as output:
                csv_writer = csv.writer(
                    output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL
                )
                # header
                row = ['Fusion', 'Databases', 'Score', 'Explained score']
                row.extend([x for x in sorted(self.__manager.get_running_tools())])
                csv_writer.writerow(row)
                for fusion in self.__manager.get_fusions():
                    row = [
                        fusion.get_name(),
                        ','.join(fusion.get_databases()),
                        fusion.get_score(),
                        fusion.get_score_explained(),
                    ]
                    for tool in sorted(self.__manager.get_running_tools()):
                        if tool not in fusion.get_tools().keys():
                            row.append('')
                        else:
                            ';'.join([
                                f'{key}: {value}' for key, value in fusion.get_tools()[tool].items()
                            ])
                    csv_writer.writerow(row)
        else:
            Logger().get_logger().error('Export output %s not supported', extension)

    def __generate_fusion_list(self, path: str, cutoff: int):
        """
        Helper function that generates file containing list of found fusions and filtered list of
        fusions. One of these files ise used by FusionInspector to visualize the fusions.
        Input for FusionInspector expects list of fusions in format `geneA--geneB\n`.

        Returns:
            - fusions_list.tsv
            - fusions_list_filtered.tsv
        """
        # unfiltered list
        with open(os.path.join(path, 'fusion_list.tsv'), 'w', encoding='utf-8') as output:
            for fusion in self.__manager.get_fusions():
                output.write(f'{fusion.get_name()}\n')

        # filtered list
        with open(os.path.join(path, 'fusion_list_filtered.tsv'), 'w', encoding='utf-8') as output:
            for fusion in self.__manager.get_fusions():
                if len(fusion.get_tools()) >= cutoff:
                    output.write(f'{fusion.get_name()}\n')

    def __score(self, params: Dict[str, Any]) -> None:
        """Custom scoring function for individual fusion.
        More information about the scoring function can be found in the documentation
        at https://github.com/matq007/fusion-report/docs/scoring-fusion
        """

        for fusion in self.__manager.get_fusions():

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

    @staticmethod
    def generate_multiqc(path: str, fusions: List[Fusion],
                         sample_name: str, running_tools_count: int) -> None:
        """Helper function that generates MultiQC Fusion section (`fusion_genes_mqc.json`)."""

        counts: Dict[str, int] = {'together': 0}
        for fusion in fusions:
            tools = fusion.get_tools()
            if len(tools) == running_tools_count:
                counts['together'] += 1
            for tool in tools:
                if tool not in counts.keys():
                    counts[tool] = 1
                else:
                    counts[tool] += 1

        configuration = {
            'id': 'fusion_genes',
            'section_name': 'Fusion genes',
            'description': 'Number of fusion genes found by various tools',
            'plot_type': 'bargraph',
            'pconfig': {
                'id': 'barplot_config_only',
                'title': 'Detected fusion genes',
                'ylab': 'Number of detected fusion genes'
            },
            'data': {
                sample_name: counts
            }
        }

        dest = f"{os.path.join(path, 'fusion_genes_mqc.json')}"
        with open(dest, 'w', encoding='utf-8') as output:
            output.write(rapidjson.dumps(configuration))
