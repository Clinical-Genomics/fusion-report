from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Pizzly(AbstractFusionTool):

    def parse(self, line, delimiter='\t'):
        col = line.strip().split(delimiter)
        fusion = f"{col[0]}--{col[2]}"
        details = {
            'pair_count': int(col[4]),
            'split_count': int(col[5])
        }

        return fusion, details
