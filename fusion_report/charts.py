""" Module containing chart definitions. """
def tool_detection_chart(counts, tools):
    """Returns tuple tool and sum of fusions found by the tool.

    Args:
        counts (dict): (tool:#count)
        tools (list): List of specified tools
    Returns:
        list: tool: #count, i.e: ['ericscript': 5, ...]
    """
    return [
        [str(tool), count] for tool, count in counts.items() if tool in tools or tool == 'together'
    ]

def create_ppi_graph(data):
    """
    Helper function that generates Network map of Protein-Protein Interactions using Cytoscape.js.
    Additional module: https://github.com/cytoscape/cytoscape.js-cose-bilkent

    Args:
        data (dict): SQL result
    Returns:
        list: Object structure which is defined by the Cytoscape library
    """
    graph_data = []
    if not data:
        return graph_data

    graph_data = [
        {'data': {'id': 'fusion'}, 'classes': 'core'},
        {'data': {'id': data[0]['h_gene']}, 'classes': 'core'},
        {'data': {'id': data[0]['t_gene']}, 'classes': 'core'},
        {'data': {
            'id': 'fusion' + data[0]['h_gene'],
            'source': 'fusion',
            'target': data[0]['h_gene']
        },
         'classes': 'core-connection'
        },
        {'data': {
            'id': 'fusion' + data[0]['t_gene'],
            'source': 'fusion',
            'target': data[0]['t_gene']
        },
         'classes': 'core-connection'
        },
    ]

    left_fusion = set(map(str.strip, data[0]['h_gene_interactions'].split(',')))
    right_fusion = set(map(str.strip, data[0]['t_gene_interactions'].split(',')))
    intersect = left_fusion & right_fusion
    left_fusion -= intersect
    right_fusion -= intersect

    # Create nodes related to left gene of the fusion
    for gene in left_fusion:
        graph_data.append({'data': {'id': gene}})
        graph_data.append({
            'data': {
                'id': gene + '--' + data[0]['h_gene'],
                'source': data[0]['h_gene'],
                'target': gene
            }
        })

    # Create nodes related to right gene of the fusion
    for gene in right_fusion:
        graph_data.append({'data': {'id': gene}})
        graph_data.append({
            'data': {
                'id': gene + '--' + data[0]['t_gene'],
                'source': data[0]['t_gene'],
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

def known_vs_unknown_chart(known, unknown):
    """Returns list of number of known  and unknown fusions.

    Args:
        known (int): Known fusions
        unknown (int): Unknown fusions
    Returns:
        list: List of known and unknown fusions found in local databases, i.e: ['known': 10, ...]
    """
    return [['known', known], ['unknown', unknown]]

def distribution_chart(fusions, tools):
    """Returns distribution of tools that found fusions.

    Args:
        fusions (dict): (fusion:FusionDetail)
        tools (list): List of specified tools
    Returns:
        list: Distribution of detection per tool, i.e: ['1 tool': 10, '2 tools': 4, ...]
    """
    data = [0] * len(tools)
    for _, fusion_details in fusions:
        data[len(fusion_details.tools) - 1] += 1

    return [[f"{index + 1} tool/s", data[index]] for index in range(len(data))]
