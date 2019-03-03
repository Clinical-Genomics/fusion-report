#!/usr/bin/env python3
def tool_detection_chart(counts, tools):
    return [[str(tool), count] for tool, count in counts.items() if tool in tools or tool == 'together']

def known_vs_unknown_chart(known, unknown):
    return [['known', known], ['unknown', unknown]]

def distribution_chart(fusions, tools):
    data = [0] * len(tools)
    for _, fusion_details in fusions.items():
        data[len(fusion_details) - 1] += 1

    return [[f"{index + 1} tool/s", data[index]] for index in range(len(data))]

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
