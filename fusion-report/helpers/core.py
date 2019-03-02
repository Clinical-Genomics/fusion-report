#!/usr/bin/env python3
import yaml

def parse_summary(p_summary):
    """
    Helper function for parsing summary.yaml
    Args:
        p_summary (string): summary.yaml
    """
    try:
        with open(p_summary, 'r') as in_file:
            return yaml.safe_load(in_file.read())
    except IOError:
        exit('File ' + p_summary + ' was not found!')

def create_tool_detection_chart(p_summary):
    """
    Helper function that generates Tool detection graph
    Args:
        p_summary (dictionary): parsed summary.yaml
    """
    result = []
    all_fusions = []
    for tool, fusions in p_summary.items():
        all_fusions.append(fusions)
        result.append([tool, len(fusions)])
    result.append(['all tools', len(set.intersection(*map(set, all_fusions)))])

    return result

def create_ppi_graph(p_data):
    """
    Helper function that generates Network map of Protein-Protein Interactions
    Args:
        p_data (SQL result): Data selected from local DB
    """
    graph_data = []
    if not p_data:
        return graph_data

    # Template for the graph generated using Cytospace.js
    # https://github.com/cytoscape/cytoscape.js-cose-bilkent
    graph_data = [
        {'data': {'id': 'fusion'}, 'classes': 'core'},
        {'data': {'id': p_data[0]['h_gene']}, 'classes': 'core'},
        {'data': {'id': p_data[0]['t_gene']}, 'classes': 'core'},
        {'data': {
            'id': 'fusion' + p_data[0]['h_gene'],
            'source': 'fusion',
            'target': p_data[0]['h_gene']
        },
         'classes': 'core-connection'
        },
        {'data': {
            'id': 'fusion' + p_data[0]['t_gene'],
            'source': 'fusion',
            'target': p_data[0]['t_gene']
        },
         'classes': 'core-connection'
        },
    ]

    left_fusion = set(map(str.strip, p_data[0]['h_gene_interactions'].split(',')))
    right_fusion = set(map(str.strip, p_data[0]['t_gene_interactions'].split(',')))
    intersect = left_fusion & right_fusion
    left_fusion -= intersect
    right_fusion -= intersect

    # Create nodes related to left gene of the fusion
    for gene in left_fusion:
        graph_data.append({'data': {'id': gene}})
        graph_data.append({
            'data': {
                'id': gene + '--' + p_data[0]['h_gene'],
                'source': p_data[0]['h_gene'],
                'target': gene
            }
        })

    # Create nodes related to right gene of the fusion
    for gene in right_fusion:
        graph_data.append({'data': {'id': gene}})
        graph_data.append({
            'data': {
                'id': gene + '--' + p_data[0]['t_gene'],
                'source': p_data[0]['t_gene'],
                'target': gene
            }
        })

    # Some fusions have common gene that can fusion with both left and right gene.
    for gene in list(intersect):
        graph_data.append({'data': {'id': gene}})
        graph_data.append({
            'data': {
                'id': 'fusion' + '--' + gene,
                'source': 'fusion',
                'target': gene
            }
        })

    return graph_data

def create_distribution_chart(p_summary):
    """
    Helper function that generates Tool distribution chart
    Args:
        p_summary (dictionary): parsed summary.yaml
    """
    graph_data = [set() for i in range(len(p_summary.keys()))]
    all_fusions = [fusions for _, fusions in p_summary.items()]
    all_fusions = sum(all_fusions, [])
    for fusion in all_fusions:
        index = all_fusions.count(fusion)
        graph_data[index - 1].add(fusion)

    return [[str(index + 1) + ' tool/s', len(value)] for index, value in enumerate(graph_data)]

def create_fusions_table(p_summary, p_known_fusions, cutoff):
    """
    Helper function that generates Fusion table
    Args:
        p_summary (dictionary): parsed summary.yaml
        p_known_fusions (list): list of all known fusions found in the local database
        cutoff (int): If not defined, using the default TOOL_DETECTION_CUTOFF
    """
    fusions = {}
    all_fusions = [fusions for _, fusions in p_summary.items()]
    unique_fusions = set(sum(all_fusions, []))

    for fusion in unique_fusions:
        tools = [fusion in x for x in all_fusions]
        summary_tools = len(p_summary.keys())
        # Add only fusions that are detected by at least <cutoff>, default = TOOL_DETECTION_CUTOFF
        # If # of tools is less than cutoff => ignore
        if sum(tools) >= cutoff or summary_tools < cutoff:
            fusions[fusion] = {
                'known': fusion in p_known_fusions,
                'tools': tools,
                'tools_total': sum(tools)
            }

    return {'fusions': fusions, 'tools': p_summary.keys()}
