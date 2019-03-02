class Starfusion():
    def __init__(self, file):
        self.__fusions = {}
        self.parse(file)

    def parse(self, file):
        try:
            with open(file, 'r') as in_file:
                next(in_file) # skip header
                for row in in_file:
                    col = row.split('\t')
                    fusion = f"{col[0]}"
                    details = {
                        'position': f"{col[5]}#{col[7]}",
                        'junction_reads': int(col[1]),
                        'spanning_reads': int(col[2]),
                        'ffmp': float(col[11])
                    }
                    if fusion not in self.__fusions:
                        self.__fusions[fusion] = []
                    
                    self.__fusions[fusion].append(details)
                        
        except IOError as error:
            print(error)
    
    def get_fusions(self):
        return self.__fusions
