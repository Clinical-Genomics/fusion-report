import sys
import os
from rapidjson import dumps

class ToolParser():
    
    def __init__(self):
        self.__fusions = {}
        self.__tools = []

    def parse(self, tool, file):
        if not file:
            print(f"File '{file}' for {tool} tool is missing , skipping ...")
        else:
            # add tool into list of using tools
            self.__tools.append(tool)
            try:
                with open(file, 'r') as in_file:
                    next(in_file) # skip header
                    for line in in_file:
                        func = getattr(self, tool) # get function from parameter
                        fusion, details = func(line.strip().split('\t')) # call function
                        
                        # check if we actually got something back
                        if fusion == None or details == None:
                            continue

                        if fusion in self.__fusions:
                            if tool in self.__fusions[fusion]:
                                self.__fusions[fusion][tool].append(details)
                            else:
                                self.__fusions[fusion][tool] = [details]
                        else:
                            self.__fusions[fusion] = { tool: [details] }
            except IOError as error:
                print(error)

    def get_fusions(self):
        return self.__fusions

    def get_tools(self):
        return self.__tools

    def get_unique_fusions(self):
        return set(self.__fusions.keys())

    def get_tools_count(self):
        counts = { tool:0 for tool in self.__tools }
        counts['together'] = 0
        for fusion, tool_list in self.__fusions.items():
            if len(tool_list) == len(self.__tools):
                counts['together'] += 1

            for tool in tool_list:
                counts[tool] += 1
        return counts

    def save(self, path, file_name):
        try:
            if self.__fusions:
                dest = f"{os.path.join(path, file_name)}.json"
                with open(dest, 'w') as output:
                    output.write(dumps(self.__fusions))
        except IOError as error:
            print(error)

    def ericscript(self, col):
        """Extracting fusions from EricScript output file
        Args:
            col (list): List of columns of a single line
        """
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

        return fusion, details

    def fusioncatcher(self, col):
        """Extracting fusions from FusionCatcher output file
        Args:
            col (list): List of columns of a single line
        """
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
    
    def pizzly(self, col):
        """Extracting fusions from Pizzly output file
        Args:
            col (list): List of columns of a single line
        """
        fusion = f"{col[0]}--{col[2]}"
        details = {
            'pair_count': int(col[4]),
            'split_count': int(col[5])
        }

        return fusion, details

    def squid(self, col):
        # check for type
        if col[10].strip() == 'non-fusion-gene':
            return None, None

        fusion = '--'.join(map(str.strip, col[11].split(':')))
        details = {
            'position': f"{col[0]}:{col[1]}-{col[2]}:{col[8]}#{col[3]}:{col[4]}-{col[5]}:{col[9]}".replace('chr', ''),
            'score': int(col[7])
        }
        
        return fusion, details
    
    def starfusion(self, col):
        """Extracting fusions from STAR-Fusion output file
        Args:
            col (list): List of columns of a single line
        """
        fusion = f"{col[0]}"
        details = {
            'position': f"{col[5]}#{col[7]}".replace('chr', ''),
            'junction_reads': int(col[1]),
            'spanning_reads': int(col[2]),
            'ffmp': float(col[11])
        }

        return fusion, details
