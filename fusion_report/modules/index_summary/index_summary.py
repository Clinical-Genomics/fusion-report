from typing import Any, Dict, List

from fusion_report.modules.base_module import BaseModule


class CustomModule(BaseModule):

    def known_vs_unknown(self) -> List[List[Any]]:
        """Returns list of number of known  and unknown fusions.

        Returns:
            List of known and unknown fusions found in local databases, i.e: ['known': 10, ...]
        """
        all_fusions: int = len(self.manager.get_fusions())
        known_fusions: int = len(self.manager.get_known_fusions())
        return [
            ['known', known_fusions],
            ['unknown', all_fusions - known_fusions]
        ]

    def tool_detection(self) -> List[List[Any]]:
        """Returns tuple tool and sum of fusions found by the tool.

        Returns:
            List of tool counts, i.e: ['ericscript': 5, ...]
        """
        running_tools = sorted(self.manager.get_running_tools())
        counts: Dict[str, int] = dict.fromkeys(running_tools, 0)
        counts['together']: int = 0
        running_tools_count: int = len(running_tools)
        for fusion in self.manager.get_fusions():
            fusion_tools = fusion.get_tools().keys()
            for tool in fusion_tools:
                counts[tool] += 1
            # intersection
            if len(fusion_tools) == running_tools_count:
                counts['together'] += 1

        return [[k, v] for k, v in counts.items()]

    def detection_distribution(self) -> List[List[Any]]:
        """Returns distribution of tools that found fusions.

        Returns:
            Distribution of detection per tool i.e: ['0 tools': 15, '1 tool': 10, '2 tools': 4, ...]
        """
        counts = [0] * (len(self.manager.get_running_tools()) + 1)
        for fusion in self.manager.get_fusions():
            counts[len(fusion.get_tools().keys())] += 1

        return [[f"{index} tool/s", counts[index]] for index in range(len(counts))]

    def create_fusions_table(self) -> Dict[str, Any]:
        """Helper function that generates fusion table.

        Returns:
            Dictionary of:
            rows: each row contains fusion information
            tools: list of executed fusion detection tools
        """
        rows = []
        tools = self.manager.get_running_tools()
        filter_flag = len(tools) < self.params['tool_cutoff']
        for fusion in self.manager.get_fusions():
            row = {}
            # If number of executed fusion detection tools is lower than cutoff, filter is ignored
            if filter_flag:
                row = {
                    'fusion': fusion.get_name(),
                    'found_db': fusion.get_databases(),
                    'tools_hits': len(fusion.get_tools()),
                    'score': f'{fusion.get_score():.3}'
                }
            # Add only fusions that are detected by at least <cutoff>
            # default = TOOL_DETECTION_CUTOFF
            if not filter_flag and len(fusion.get_tools()) >= self.params['tool_cutoff']:
                row = {
                    'fusion': fusion.get_name(),
                    'found_db': fusion.get_databases(),
                    'tools_hits': len(fusion.get_tools()),
                    'score': f'{fusion.get_score():.3}'
                }

            # Add only if row is not empty
            if bool(row):
                for tool in tools:
                    row[tool] = 'true' if tool in sorted(fusion.get_tools()) else 'false'
                rows.append(row)

        return {
            'rows': rows,
            'tools': list(sorted(tools))
        }

    def load(self) -> Dict[str, Any]:
        """Return module variables."""

        return {
            'tools': self.manager.get_running_tools(),
            'num_detected_fusions': len(self.manager.get_fusions()),
            'num_known_fusions': len(self.manager.get_known_fusions()),
            'tool_detection_graph': self.tool_detection(),
            'known_vs_unknown_graph': self.known_vs_unknown(),
            'distribution_graph': self.detection_distribution(),
            'fusion_list': self.create_fusions_table(),
            'tool_cutoff': self.params['tool_cutoff'],
            'menu': [
                'Dashboard fusion summary',
                'List of detected fusions'
            ]
        }
