""" Helper class for ToolParser. """
class FusionDetail:
    """ Class for defining structure of fusion detail. """
    def __init__(self):
        self.score = 0.0
        self.score_explained = ''
        self.tools = {}
        self.dbs = []

    def add_tool(self, tool, details):
        """
        Method for adding fusion detection tool with its info about fusion to the list.

        Args:
            tool (str): Name of the tool
            details (dict): Detail description of fusion from a defined tool
        """
        if tool not in self.tools.keys():
            self.tools[tool] = []
        self.tools[tool].append(details)

    def add_db(self, db_name):
        """
        Method for adding database name which found the fusion.

        Args:
            db_name (str): database name
        """
        if db_name not in self.dbs:
            self.dbs.append(db_name)
