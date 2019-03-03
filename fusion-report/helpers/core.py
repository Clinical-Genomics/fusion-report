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

def create_fusions_table(fusions, tools, known_fusions, cutoff):
    """
    Helper function that generates Fusion table
    Args:
        
        cutoff (int): If not defined, using the default TOOL_DETECTION_CUTOFF
    """
    rows = []
    for fusion, fusion_details in fusions.items():
        # Add only fusions that are detected by at least <cutoff>, default = TOOL_DETECTION_CUTOFF
        # If # of tools is less than cutoff => ignore
        if len(tools) >= cutoff or len(fusion_details.keys()) < cutoff:
            row = {
                'fusion': fusion,
                'found_db': 'true' if fusion in known_fusions else 'false',
                'tools_hits': len(fusion_details.keys())
            }
            for tool in tools:
                row[tool] = 'true' if tool in fusion_details.keys() else 'false'
            rows.append(row)

    return {'fusions': rows, 'tools': tools}
