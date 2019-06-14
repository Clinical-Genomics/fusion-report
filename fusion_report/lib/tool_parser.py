""" Module for tool parser. """
import os
import sys
import rapidjson
from fusion_report.lib.fusion_detail import FusionDetail

class ToolParser():
    """ Class for processing output from fusion tools. """
    def __init__(self):
        self.__fusions = {}
        self.__tools = []

    def parse(self, tool, file):
        """
        Method for processing output from fusion tool.

        Args:
            tool (str): Fusion tool name
            file (str): Output filename
        """
        if self.verify(file):
            # add tool into list of using tools
            self.__tools.append(tool)
            try:
                with open(file, 'r', encoding='utf-8') as in_file:
                    next(in_file) # skip header
                    for line in in_file:
                        func = getattr(self, tool) # get function from parameter
                        fusion, details = func(line.strip().split('\t')) # call function

                        # check if we actually got something back
                        if fusion is None or details is None:
                            continue

                        if fusion not in self.__fusions.keys():
                            self.__fusions[fusion] = FusionDetail()

                        self.__fusions[fusion].add_tool(tool, details)
            except IOError as error:
                sys.exit(error)
        else:
            print(f"Skipping {tool}, due to missing {file}")

    def get_fusion(self, fusion):
        """
        Method for getting a specific fusion by name.

        Args:
            fusion (str): Name of the fusion
        Returns:
            dict: (fusion:FusionDetail)
        """
        return {} if fusion not in self.__fusions.keys() else self.__fusions[fusion]

    def get_fusions(self):
        """
        Method for returning fusions

        Returns:
            dict_items
        """
        return self.__fusions.items()

    def get_unique_fusions(self):
        """ Return list of unique fusions. """
        return set(self.__fusions.keys())

    def get_tools(self):
        """
        Method for returning list of used fusion tools.

        Returns:
            list: List of used tools
        """
        return self.__tools

    def get_tools_count(self):
        """
        Method for counting how many fusions were found by which tool.

        Returns:
            dict: (tool: number of fusions)
        """
        counts = {tool:0 for tool in self.get_tools()}
        counts['together'] = 0
        for _, fusion_detail in self.get_fusions():
            if len(fusion_detail.tools) == len(self.get_tools()):
                counts['together'] += 1

            for tool in fusion_detail.tools:
                counts[tool] += 1
        return counts

    def get_db_counts(self):
        """Get list of known and unknown fusion genes derived from provided databases."""
        known_fusions = 0
        unknown_fusion = 0
        for _, detail in self.get_fusions():
            if not detail.dbs:
                unknown_fusion += 1
            else:
                known_fusions += 1

        return known_fusions, unknown_fusion

    def save(self, path, file_name):
        """
        Method for saving fusion structure into json.

        Args:
            path (str): Path
            file_name (str): Name of the file
        """
        try:
            if self.__fusions:
                dest = f"{os.path.join(path, file_name)}.json"
                res = {}
                for fusion, fusion_detail in self.get_fusions():
                    res[fusion] = vars(fusion_detail)
                with open(dest, 'w', encoding='utf-8') as output:
                    output.write(rapidjson.dumps(res))
        except IOError as error:
            sys.exit(error)

    @staticmethod
    def verify(file):
        """
        Method for checking if provided file exists

        Args:
            file (str): Input file name
        """
        return os.path.exists(file) and os.stat(file).st_size > 0

    @staticmethod
    def ericscript(col):
        """
        Function for parsing output from EricScript.

        Args:
            col (list): List of columns of a single line
        Returns:
            tuple: fusion (str) and details (dict)
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

    @staticmethod
    def fusioncatcher(col):
        """
        Function for parsing output from FusionCatcher.

        Args:
            col (list): List of columns of a single line
        Returns:
            tuple: fusion (str) and details (dict)
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

    @staticmethod
    def pizzly(col):
        """
        Function for parsing output from Pizzly.

        Args:
            col (list): List of columns of a single line
        Returns:
            tuple: fusion (str) and details (dict)
        """
        fusion = f"{col[0]}--{col[2]}"
        details = {
            'pair_count': int(col[4]),
            'split_count': int(col[5])
        }

        return fusion, details

    @staticmethod
    def squid(col):
        """
        Function for parsing output from Squid.

        Args:
            col (list): List of columns of a single line
        Returns:
            tuple: fusion (str) and details (dict)
        """
        # check for type
        if col[10].strip() == 'non-fusion-gene':
            return None, None

        fusion = '--'.join(map(str.strip, col[11].split(':')))
        left_breakpoint = f"{col[0]}:{col[1]}-{col[2]}:{col[8]}".replace('chr', '')
        right_breakpoint = f"{col[3]}:{col[4]}-{col[5]}:{col[9]}".replace('chr', '')
        details = {
            'position': f"{left_breakpoint}#{right_breakpoint}" if col[8] == '+'
                        else f"{right_breakpoint}#{left_breakpoint}",
            'score': int(col[7])
        }

        return fusion, details

    @staticmethod
    def starfusion(col):
        """
        Function for parsing output from STAR-Fusion.

        Args:
            col (list): List of columns of a single line
        Returns:
            tuple: fusion (str) and details (dict)
        """
        fusion = f"{col[0]}"
        details = {
            'position': f"{col[5]}#{col[7]}".replace('chr', ''),
            'junction_reads': int(col[1]),
            'spanning_reads': int(col[2]),
            'ffmp': float(col[11])
        }

        return fusion, details

    @staticmethod
    def dragen(col):
        """
        Function for parsing output from Dragen.

        Args:
            col (list): List of columns of a single line
        Returns:
            tuple: fusion (str) and details (dict)
        """
        fusion = f"{col[0]}"
        details = {
            'position': f"{col[2]}#{col[3]}".replace('chr', ''),
            'score': int(col[1])
        }

        return fusion, details
