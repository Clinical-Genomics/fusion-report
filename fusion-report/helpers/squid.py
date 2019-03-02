class Squid():
    def __init__(self, file):
        self.__fusions = {}
        self.parse(file)

    def parse(self, file):
        try:
            with open(file, 'r') as in_file:
                next(in_file) # skip header
                for row in in_file:
                    col = row.split('\t')
                    # type 
                    if col[10].strip() == 'non-fusion-gene':
                        continue
                    fusion = '--'.join(map(str.strip, col[11].split(':')))
                    details = {
                        'position': f"{col[0]}:{col[1]}-{col[2]}:{col[8]}#{col[3]}:{col[4]}-{col[5]}:{col[9]}".replace('chr', ''),
                        'score': int(col[7])
                    }
                    if fusion not in self.__fusions:
                        self.__fusions[fusion] = []
                    
                    self.__fusions[fusion].append(details)
                        
        except IOError as error:
            print(error)
    
    def get_fusions(self):
        return self.__fusions
