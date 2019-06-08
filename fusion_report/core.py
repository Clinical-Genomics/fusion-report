"""Module contains all core functions."""
import os
import sys
import re

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
        sys.exit(error)

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
