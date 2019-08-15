from fusion_report.parsers.abstract_fusion import AbstractFusionTool


class Squid(AbstractFusionTool):

    def parse(self, line, delimiter='\t'):
        col = line.strip().split(delimiter)
        if col[10].strip() == 'non-fusion-gene':
            return None, None

        fusion = '--'.join(map(str.strip, col[11].split(':')))
        left_breakpoint = f"{col[0]}:{col[1]}-{col[2]}:{col[8]}".replace('chr', '')
        right_breakpoint = f"{col[3]}:{col[4]}-{col[5]}:{col[9]}".replace('chr', '')
        details = {
            'position': f"{left_breakpoint}#{right_breakpoint}"
                        if col[8] == '+' else f"{right_breakpoint}#{left_breakpoint}",
            'score': int(col[7])
        }
        return fusion, details
