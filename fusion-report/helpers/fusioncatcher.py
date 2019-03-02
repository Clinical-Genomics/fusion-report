class Fusioncatcher():
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
                        'position': f"{col[8]}#{col[9]}",
                        'common_mapping_reads': int(col[3]),
                        'spanning_pairs': int(col[4]),
                        'spanning_unique_reads': int(col[5]),
                        'longest_anchor': int(col[6]),
                        'fusion_type': col[15].strip()
                    }
                    if fusion not in self.__fusions:
                        self.__fusions[fusion] = []
                    
                    self.__fusions[fusion].append(details)
                        
        except IOError as error:
            print(error)
    
    def get_fusions(self):
        return self.__fusions
