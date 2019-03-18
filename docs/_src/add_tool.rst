Add new tool
============

ToolParser is class responsible for parsing the output from different fusion detection tools.
To add a new tool to the stack you have to (replace <tool-name> with an actual name of the tool):
**TL;DR:** make sure you use the **same name everywhere** otherwise the application will not be
able to detect and invoke the tool.

1. Create two arguments parameters in `bin/fusion_report`.

.. code-block:: python

    # Tool
    tools.add_argument(
        '--<tool-name>',
        help='<tool-name> output file',
        type=str
    )

    # Weight
    tools.add_argument(
        '--<tool-name>_weight',
        help='<tool-name> weight',
        type=float,
        default=DEFAULT_TOOL_WEIGHT
    )

2. Add the tool to `SUPPORTED_TOOLS` list in `bin/fusion_report`.

.. code-block:: python
    
    SUPPORTED_TOOLS = ['ericscript', 'starfusion', 'fusioncatcher', 'pizzly', 'squid', <tool-name>]

3. Create a static method to parse a line (header is skipped automatically) in fusion_report/helpers/tool_parser.py.
   The function has to return name of the fusion and any additional info provided by the tool. The details parameter
   can have any attributes, there are no real limitations here. See EricScript example below:

.. code-block:: python

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

4. Write tests to make sure everything works
5. Make a pull request (PR) so everyone else can use it as well!