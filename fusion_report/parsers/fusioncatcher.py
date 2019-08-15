from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Fusioncatcher(AbstractFusionTool):

    def parse(self, line, delimiter='\t'):
        col = line.strip().split(delimiter)
        fusion = f"{col[0]}--{col[1]}"
        details = {
            'position': f"{col[8]}#{col[9]}",
            'common_mapping_reads': int(col[3]),
            'spanning_pairs': int(col[4]),
            'spanning_unique_reads': int(col[5]),
            'longest_anchor': int(col[6]),
            'fusion_type': col[15].strip()
        }

        return fusion, details
