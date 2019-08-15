from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Starfusion(AbstractFusionTool):

    def parse(self, line, delimiter='\t'):
        col = line.strip().split(delimiter)
        fusion = f"{col[0]}"
        details = {
            'position': f"{col[5]}#{col[7]}",
            'junction_reads': int(col[1]),
            'spanning_reads': int(col[2]),
            'ffmp': float(col[11])
        }
        return fusion, details
