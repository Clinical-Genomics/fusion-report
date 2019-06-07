"""Module contains all utility helper functions."""
import os
import rapidjson
from fusion_report.lib.tool_parser import ToolParser

__version__ = '1.0.0'

def parse(params, supported_tools):
    """
    Function calling parser of individual tool.

    Args:
        params (ArgumentParser):
    """
    tools = ToolParser()
    for tool in supported_tools:
        tools.parse(tool, params.__dict__[tool])

    return tools

def print_progress_bar(iteration, total, length=50, fill='='):
    """
    Call in a loop to create terminal progress bar.
    Taken from: https://stackoverflow.com/a/34325723

    Args:
        iteration (int): current iteration
        total (int): total iterations
        length (int): character length of progress bar
        fill (str): progress bar fill character
    Returns:
        str: Progress bar
    """
    if total > 0:
        percent = int(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        progress_bar = fill * filled_length + '-' * (length - filled_length)
        print('\rProgress |%s| %s%% Complete' % (progress_bar, percent), end='\r')
        # Print New Line on Complete
        if iteration == total:
            print()

def create_multiqc_section(path, tool_counts, sample_name):
    """
    Helper function that generates fusion table.

    Args:
        path (str)
        tool_counts (dict): (tool: number of fusions)
        sample_name (str): name of the sample

    Returns:
        Generates `fusions_mqc.json`
    """
    print('[MultiQC]: generating bar-plot of found fusions')
    configuration = {
        'id': 'fusion_genes',
        'section_name': 'Fusion genes',
        'description': 'Number of fusion genes found by various tools',
        'plot_type': 'bargraph',
        'pconfig': {
            'id': 'barplot_config_only',
            'title': 'Detected fusion genes',
            'ylab': 'Number of detected fusion genes'
        },
        'data': {
            sample_name: tool_counts
        }
    }
    try:
        dest = f"{os.path.join(path, 'fusions_mqc.json')}"
        with open(dest, 'w', encoding='utf-8') as output:
            output.write(rapidjson.dumps(configuration))
    except IOError as error:
        exit(error)
