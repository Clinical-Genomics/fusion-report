from typing import Any, Dict, List

from fusion_report.modules.base_module import BaseModule


class CustomModule(BaseModule):

    def known_vs_unknown(self) -> List[List[Any]]:
        """Returns list of number of known  and unknown fusions.

        Returns:
            List of known and unknown fusions found in local databases, i.e: ['known': 10, ...]
        """
        all_fusions: int = len(self.manager.fusions)
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
        running_tools = sorted(self.manager.running_tools)
        counts: Dict[str, int] = dict.fromkeys(running_tools, 0)
        counts['together'] = 0
        running_tools_count: int = len(running_tools)
        for fusion in self.manager.fusions:
            print(fusion.name)
            fusion_tools = fusion.tools.keys()
            for tool in fusion_tools:
                print(tool)
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
        counts = [0] * (len(self.manager.running_tools) + 1)
        for fusion in self.manager.fusions:
            counts[len(fusion.tools.keys())] += 1

        return [[f"{index} tool/s", counts[index]] for index in range(len(counts))]

    def create_fusions_table(self) -> Dict[str, Any]:
        """Helper function that generates fusion table.

        Returns:
            Dictionary of:
            rows: each row contains fusion information
            tools: list of executed fusion detection tools
        """
        rows = []
        tools = self.manager.running_tools
        filter_flag = len(tools) < self.params['tool_cutoff']
        for fusion in self.manager.fusions:
            row: Dict[str, Any] = {}
            # If number of executed fusion detection tools is lower than cutoff, filter is ignored
            if filter_flag:
                row = {
                    'fusion': fusion.name,
                    'found_db': fusion.dbs,
                    'tools_hits': len(fusion.tools),
                    'score': f'{fusion.score:.3}'
                }
            # Add only fusions that are detected by at least <cutoff>
            # default = TOOL_DETECTION_CUTOFF
            if not filter_flag and len(fusion.tools) >= self.params['tool_cutoff']:
                row = {
                    'fusion': fusion.name,
                    'found_db': fusion.dbs,
                    'tools_hits': len(fusion.tools),
                    'score': f'{fusion.score:.3}'
                }

            # Add only if row is not empty
            if bool(row):
                for tool in tools:
                    row[tool] = 'true' if tool in sorted(fusion.tools) else 'false'
                rows.append(row)

        return {
            'rows': rows,
            'tools': list(sorted(tools))
        }

    def load(self) -> Dict[str, Any]:
        """Return module variables."""

        return {
            'tools': self.manager.running_tools,
            'num_detected_fusions': len(self.manager.fusions),
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
