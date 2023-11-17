"""Main app module"""
import csv
import os
import sys
import time

from argparse import Namespace
from collections import defaultdict
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
from fusion_report.data.fusiongdb2 import FusionGDB2
from fusion_report.data.mitelman import MitelmanDB
from fusion_report.download import Download
from fusion_report.settings import Settings
from fusion_report.sync import Sync


class App:
    """The class implements core methods.

    Attributes:
        manager: Fusion manager
        args: Parsed settings
    """

    def __init__(self) -> None:
        try:
            self.args = ArgsBuilder()
            self.manager = FusionManager(self.args.supported_tools)
        except IOError as ex:
            raise AppException(ex)

    def build_args(self):
        """Builds command-line arguments."""
        self.args.build()

    def run(self):
        """Parse parameters and execute commands.

        Raises:
            AppException
        """
        params = self.args.parse()
        try:
            if params.command == "run":
                Logger(__name__).info("Running application...")
                self.preprocess(params)
                self.generate_report(params)
                self.export_results(params.output, params.export)
                self.generate_multiqc(
                    params.output,
                    self.manager.fusions,
                    params.sample,
                    len(self.manager.running_tools),
                )
                self.generate_fusion_list(params.output, params.tool_cutoff)
            elif params.command == "download":
                Logger(__name__).info("Downloading resources...")
                Download(params)
            elif params.command == "sync":
                Logger(__name__).info("Synchronizing databases...")
                Sync(params)
            else:
                sys.exit(f"Command {params.command} not recognized!")
        except (AppException, DbException, DownloadException, IOError) as ex:
            raise AppException(ex)

    def preprocess(self, params: Namespace) -> None:
        """Parse, enrich and score fusion."""
        self.parse_fusion_outputs(vars(params))
        self.enrich(params.db_path)
        self.score(vars(params))

    def generate_report(self, params: Namespace) -> None:
        """Generate fusion report with all pages."""
        report = Report(params.config, params.output)
        fusions = [
            fusion for fusion in self.manager.fusions if len(fusion.tools) >= params.tool_cutoff
        ]

        index_page = report.create_page(
            "Summary", filename="index.html", page_variables={"sample": params.sample}
        )
        index_page.add_module(
            "index_summary", self.manager, params={"tool_cutoff": params.tool_cutoff}
        )
        report.render(index_page)

        with tqdm(total=len(fusions)) as pbar:
            for fusion in fusions:
                fusion_page = report.create_page(
                    fusion.name, page_variables={"sample": params.sample}
                )
                fusion_page.add_module("fusion_summary", params={"fusion": fusion})
                fusion_page.add_module(
                    "fusiongdb.variations",
                    params={"fusion": fusion.name, "db_path": params.db_path},
                )
                fusion_page.add_module(
                    "fusiongdb.transcripts",
                    params={"fusion": fusion.name, "db_path": params.db_path},
                )
                fusion_page.add_module(
                    "fusiongdb.ppi",
                    params={"fusion": fusion.name, "db_path": params.db_path},
                )
                fusion_page.add_module(
                    "fusiongdb.drugs",
                    params={"fusion": fusion.name, "db_path": params.db_path},
                )
                fusion_page.add_module(
                    "fusiongdb.diseases",
                    params={"fusion": fusion.name, "db_path": params.db_path},
                )
                report.render(fusion_page)
                pbar.set_description(f"Processing {fusion.name}")
                time.sleep(0.1)
                pbar.update(1)

    def parse_fusion_outputs(self, params: Dict[str, Any]) -> None:
        """Executes parsing for each provided fusion detection tool."""
        for param, value in params.items():
            if param in self.manager.supported_tools and value:
                # param: fusion tool
                # value: fusion tool output
                self.manager.parse(param, value, params["allow_multiple_gene_symbols"])

    def enrich(self, path: str) -> None:
        """Enrich fusion with all relevant information from local databases."""
        local_fusions: Dict[str, List[str]] = {
            CosmicDB(path).name: CosmicDB(path).get_all_fusions(),
            MitelmanDB(path).name: MitelmanDB(path).get_all_fusions(),
            FusionGDB(path).name: FusionGDB(path).get_all_fusions(),
            FusionGDB2(path).name: FusionGDB2(path).get_all_fusions(),
        }
        for fusion in self.manager.fusions:
            for db_name, db_list in local_fusions.items():
                if fusion.name in db_list:
                    fusion.add_db(db_name)

    def export_results(self, path: str, extension: str) -> None:
        """Export results.
        Currently supporting file types: JSON and CSV
        """
        dest = f"{os.path.join(path, 'fusions')}.{extension}"
        if extension == "json":
            with open(dest, "w", encoding="utf-8") as output:
                results = [fusion.json_serialize() for fusion in self.manager.fusions]
                output.write(rapidjson.dumps(results))
        elif extension == "csv":
            with open(dest, "w", encoding="utf-8") as output:
                csv_writer = csv.writer(
                    output, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
                )
                # header
                header = ["Fusion", "Databases", "Score", "Explained score"]
                header.extend([x for x in sorted(self.manager.running_tools)])
                csv_writer.writerow(header)
                for fusion in self.manager.fusions:
                    row: List[Any] = [
                        fusion.name,
                        ",".join(fusion.dbs),
                        fusion.score,
                        fusion.score_explained,
                    ]
                    for tool in sorted(self.manager.running_tools):
                        if tool in fusion.tools.keys():
                            row.append(
                                ",".join(
                                    [f"{key}: {value}" for key, value in fusion.tools[tool].items()]
                                )
                            )
                        else:
                            row.append("")
                    csv_writer.writerow(row)
        else:
            Logger(__name__).error("Export output %s not supported", extension)

    def generate_fusion_list(self, path: str, cutoff: int):
        """
        Helper function that generates file containing list of found fusions and filtered list of
        fusions. One of these files is used by FusionInspector to visualize the fusions.
        Input for FusionInspector expects list of fusions in format `geneA--geneB\n`.

        Returns:
            - fusions_list.tsv
            - fusions_list_filtered.tsv
        """
        # unfiltered list
        with open(os.path.join(path, "fusion_list.tsv"), "w", encoding="utf-8") as output:
            for fusion in self.manager.fusions:
                output.write(f"{fusion.name}\n")

        # filtered list
        with open(os.path.join(path, "fusion_list_filtered.tsv"), "w", encoding="utf-8") as output:
            for fusion in self.manager.fusions:
                if len(fusion.tools) >= cutoff:
                    output.write(f"{fusion.name}\n")

    def score(self, params: Dict[str, Any]) -> None:
        """Custom scoring function for individual fusion.
        More information about the scoring function can be found in the documentation
        at https://github.com/matq007/fusion-report/docs/scoring-fusion
        """

        for fusion in self.manager.fusions:
            # tool estimation
            tool_score: float = sum(
                [params[f"{tool.lower()}_weight"] / 100.0 for tool, _ in fusion.tools.items()]
            )
            tool_score_expl: List[str] = [
                format((params[f"{tool}_weight"] / 100.0), ".3f")
                for tool, _ in fusion.tools.items()
            ]

            # database estimation
            db_score: float = sum(
                float(Settings.FUSION_WEIGHTS[db_name.lower()]) for db_name in fusion.dbs
            )
            db_score_expl: List[str] = [
                format(Settings.FUSION_WEIGHTS[db_name.lower()], ".3f") for db_name in fusion.dbs
            ]

            score: float = float("%0.3f" % (0.5 * tool_score + 0.5 * db_score))
            score_explained = (
                f'0.5 * ({" + ".join(tool_score_expl)}) + 0.5 * ({" + ".join(db_score_expl)})'
            )
            fusion.score, fusion.score_explained = score, score_explained

    @staticmethod
    def generate_multiqc(
        path: str, fusions: List[Fusion], sample_name: str, running_tools_count: int
    ) -> None:
        """Helper function that generates MultiQC Fusion section (`fusion_genes_mqc.json`)."""

        counts: Dict[str, int] = defaultdict(lambda: 0)
        for fusion in fusions:
            tools = fusion.dbs
            if len(tools) == running_tools_count:
                counts["together"] += 1
            for tool in tools:
                counts[tool] += 1

        configuration = {
            "id": "fusion_genes",
            "section_name": "Fusion genes",
            "description": "Number of fusion genes found by various tools",
            "plot_type": "bargraph",
            "pconfig": {
                "id": "barplot_config_only",
                "title": "Detected fusion genes",
                "ylab": "Number of detected fusion genes",
            },
            "data": {sample_name: counts},
        }

        dest = f"{os.path.join(path, 'fusion_genes_mqc.json')}"
        with open(dest, "w", encoding="utf-8") as output:
            output.write(rapidjson.dumps(configuration))
