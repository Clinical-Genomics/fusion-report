#!/usr/bin/env python3
"""Module contains all helper functions together with all functions
for generating charts and tables.
"""
import re
import os
import rapidjson

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

def create_fusions_table(fusions, tools, cutoff):
    """
    Helper function that generates fusion table.

    Args:
        fusions (dict_items)
        tools (list): List of specified tools
        cutoff (int): Tool detection cutoff
    Returns:
        dict: fusions (dict) and tools (list)
    """
    rows = []
    filter_flag = len(tools) < cutoff
    for fusion, fusion_details in fusions:
        row = {}
        # If number of executed fusion detection tools is lower than cutoff, filter is ignored
        if filter_flag:
            row = {
                'fusion': fusion,
                'found_db': fusion_details.dbs,
                'tools_hits': len(fusion_details.tools),
                'score': f'{fusion_details.score:.3}'
            }
        # Add only fusions that are detected by at least <cutoff>, default = TOOL_DETECTION_CUTOFF
        if not filter_flag and len(fusion_details.tools) >= cutoff:
            row = {
                'fusion': fusion,
                'found_db': fusion_details.dbs,
                'tools_hits': len(fusion_details.tools),
                'score': f'{fusion_details.score:.3}'
            }

        # Add only if row is not empty
        if bool(row):
            for tool in tools:
                row[tool] = 'true' if tool in fusion_details.tools.keys() else 'false'
            rows.append(row)

    return {'fusions': rows, 'tools': tools}

def create_multiqc_section(path, tool_counts, sample_name):
    """
    Helper function that generates fusion table.

    Args:
        path (str)
        tool_counts (dict): (tool: number of fusions)
        sample_name (str): name of the sample

    Returns:
        Generates `fusion_genes_mqc.json`
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
        dest = f"{os.path.join(path, 'fusion_genes_mqc.json')}"
        with open(dest, 'w', encoding='utf-8') as output:
            output.write(rapidjson.dumps(configuration))
    except IOError as error:
        exit(error)

def create_fusion_list(path, parser, cutoff):
    """
    Helper function that generates file containing list of found fusions and filtered list of
    fusions. One of these files ise used by FusionInspector to visualize the fusions.
    Input for FusionInspector expects list of fusions in format `geneA--geneB\\n`.

    Args:
        path (str)
        parser (ToolParser)
        cutoff (int): cutoff for filtering purpose

    Returns:
        Generates:
            - fusions_list.txt
            - fusions_list_filtered.txt
    """
    print('[FusionInspector]: generating filtered and unfiltered fusion list')
    try:
        # unfiltered fusions list
        unfiltered = parser.get_unique_fusions()
        dest = f"{os.path.join(path, 'fusions_list.txt')}"
        with open(dest, 'w', encoding='utf-8') as output:
            for fusion in unfiltered:
                output.write(f'{fusion}\n')

        # filtered fusions list
        filtered = [
            fusion for fusion, details in parser.get_fusions() if len(details.tools) >= cutoff
        ]
        dest = f"{os.path.join(path, 'fusions_list_filtered.txt')}"
        with open(dest, 'w', encoding='utf-8') as output:
            for fusion in filtered:
                output.write(f'{fusion}\n')
    except IOError as error:
        exit(error)

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
    percent = int(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    progress_bar = fill * filled_length + '-' * (length - filled_length)
    print('\rProgress |%s| %s%% Complete' % (progress_bar, percent), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()

def get_db_fusions(db):
    """
    Helper function for retrieving all fusions from used databases.

    Args:
        db (Db)
    Returns:
        dict: (database_name: list of fusions)
    """
    database = {}
    db_names = db.get_db_names()
    # FusionGDB
    if 'fusiongdb' in db_names:
        db.connect('fusiongdb')
        res = db.select('''
            SELECT DISTINCT (h_gene || "--" || t_gene) as fusion_pair 
            FROM TCGA_ChiTaRS_combined_fusion_information_on_hg19
            ''')
        database['FusionGDB'] = [fusion['fusion_pair'] for fusion in res]

    # Mitelman
    if 'mitelman' in db_names:
        db.connect('mitelman')
        res = db.select('''
            SELECT DISTINCT GeneShort FROM MolBiolClinAssoc WHERE GeneShort LIKE "%/%"
            ''')
        database['Mitelman'] = [fusion['GeneShort'].strip().replace('/', '--') for fusion in res]

    # COSMIC
    if 'cosmic' in db_names:
        db.connect('cosmic')
        res = db.select('''
            SELECT DISTINCT translocation_name FROM CosmicFusionExport
            WHERE translocation_name != ""
            ''')
        database['COSMIC'] = [
            '--'.join(re.findall(r'[A-Z0-9]+(?=\{)', x['translocation_name'])) for x in res
        ]

    return database

def score_fusion(fusion_detail, params):
    """Custom scoring function for individual fusion.
    More information about the scoring function can be found in the documentation
    at https://github.com/matq007/fusion-report/docs/scoring-fusion

    Args:
        fusion_detail (FusionDetail)
        params (ArgumentParser)
    Returns:
        float: Estimate score of how genuine is the fusion.
    """

    # Tools found
    params_dict = vars(params)
    tool_score = 0.0
    score_explained = []
    for tool in fusion_detail.tools.keys():
        if f'{tool}_weight' in params_dict:
            tool_score += params_dict[f'{tool}_weight'] / 100.0
            score_explained.append(format((params_dict[f'{tool}_weight'] / 100.0), '.3f'))

    fusion_detail.score_explained = f'0.5 * ({" + ".join(score_explained)})'

    # Scoring based on DB
    score_explained = []
    db_score = 0.0
    weights = {'fusiongdb': 0.20, 'cosmic': 0.40, 'mitelman': 0.40}
    for db_name in fusion_detail.dbs:
        db_score += 1.0 * weights[db_name.lower()]
        score_explained.append(format(weights[db_name.lower()], '.3f'))

    fusion_detail.score_explained += f' + 0.5 * ({" + ".join(score_explained)})'
    total_score = tool_score * 0.5 + db_score * 0.5
    fusion_detail.score = float('%0.3f' % total_score)
