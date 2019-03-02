class Ericscript():
    def __init__(self, file):
        self.__fusions = {}
        self.parse(file)

    def parse(self, file):
        try:
            with open(file, 'r') as in_file:
                next(in_file) # skip header
                for row in in_file:
                    col = row.split('\t')
                    fusion = f"{col[0]}--{col[1]}"
                    details = {
                        'position': f"{col[2]}:{col[3]}:{col[4]}#{col[5]}:{col[6]}:{col[7]}",
                        'discordant_reads': int(col[10]),
                        'junction_reads': int(col[11]),
                        'fusion_type': col[14],
                        'gene_expr1': float(col[18]),
                        'gene_expr2': float(col[19]),
                        'gene_expr_fusion': float(col[20])
                    }
                    if fusion not in self.__fusions:
                        self.__fusions[fusion] = []
                    
                    self.__fusions[fusion].append(details)
                        
        except IOError as error:
            print(error)
    
    def get_fusions(self):
        return self.__fusions
