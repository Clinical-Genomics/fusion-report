#!/usr/bin/env python3
"""This module generates summary report for nfcore/rnafusion pipeline from all found fusion genes."""
import argparse
from db import Db
from helpers.core import *
from helpers.tool_parser import ToolParser
from lib.page import Page
from lib.report import Report
from lib.section import Section
from lib.graph import Graph

# Minimum number of tools that have to detect a fusion, used as a filter in Dashboard
TOOL_DETECTION_CUTOFF = 2

def parse(params):
    tools = ToolParser()
    tools.parse('ericscript', params.ericscript)
    tools.parse('starfusion', params.starfusion)
    tools.parse('fusioncatcher', params.fusioncatcher)
    tools.parse('pizzly', params.pizzly)
    tools.parse('squid', params.squid)
    return tools

def generate_index(params, parser, known_fusions, unknown_fusions):
    # Index page
    unknown_sum = len(unknown_fusions)
    known_sum = len(known_fusions)
    index_page = Page(
        title = 'index',
        page_variables = {
            'sample': params.sample,
            'fusions_sum': int(unknown_sum + known_sum),
            'known_fusion_sum': known_sum,
            'fusion_tools': parser.get_tools()
        },
        partial_template = 'index'
    )

    dashboard_section = Section(
        section_id = 'dashboard',
        title = 'Dashboard fusion summary'
    )
    dashboard_section.add_graph(
         Graph(
            'tool_detection_chart',
            'Tool detection',
            'Displays number of found fusions per tool.',
            tool_detection_chart(parser.get_tools_count(), parser.get_tools())
        )
    )
    dashboard_section.add_graph(
         Graph(
            'known_vs_unknown_chart',
            'Known Vs Unknown',
            'Shows the ration between found and unknown missing fusions in the local database.',
            known_vs_unknown_chart(known_sum, unknown_sum)
        )
    )
    dashboard_section.add_graph(
         Graph(
            'distribution_chart',
            'Tool detection distribution',
            'Sum of counts detected by different tools per fusion.',
            distribution_chart(parser.get_fusions(), parser.get_tools())
        )
    )
    index_page.add_section(dashboard_section)
    return index_page

def generate_fusion_page(params):
    pass

def generate_report(params):
    parser = parse(params)
    
    # TODO: check if parser is empty

    db_instance = Db(params.database)
    known_fusions = []
    unknown_fusions = []
    report = Report(params.config, params.output)

    # TODO: Possible helper function
    # Get all fusions from DB
    db_fusions = db_instance.select('''
        SELECT DISTINCT (h_gene || "--" || t_gene) as fusion_pair 
        FROM TCGA_ChiTaRS_combined_fusion_information_on_hg19
        ''')
    db_fusions = [x['fusion_pair'] for x in db_fusions]

    fusions = parser.get_fusions()
    for fusion in fusions:
        
        if fusion not in db_fusions:
            unknown_fusions.append(fusion)
            # go to next fusion
            continue

        known_fusions.append(fusion)
        # fusion_page = Page(
        #     title = fusion,
        #     page_variables = { 'sample': params.sample },
        #     partial_template = 'fusion'
        # )
    
    index_page = generate_index(params, parser, known_fusions, unknown_fusions)
    report.add_page(index_page)

# def generate(p_args):
#     """Function for generating UI friendly report"""
#     if p_args.fusions is None or p_args.summary is None:
#         exit('Fusion list or summary was not provided')

#     db_instance = Db(p_args.database)
#     known_fusions = []
#     unknown_fusions = []
#     summary_file = parse_summary(p_args.summary)
#     report = Report(p_args.config, p_args.output)

#     # Get all fusions from DB
#     db_fusions = db_instance.select('''
#         SELECT DISTINCT (h_gene || "--" || t_gene) as fusion_pair 
#         FROM TCGA_ChiTaRS_combined_fusion_information_on_hg19
#         ''')
#     db_fusions = [x['fusion_pair'] for x in db_fusions]

#     # Create page per fusion
#     with open(p_args.fusions, 'r') as fusions:
#         for fusion_pair in fusions:
#             fusion_pair = fusion_pair.rstrip()

#             if fusion_pair not in db_fusions:
#                 unknown_fusions.append(fusion_pair)
#                 continue

#             known_fusions.append(fusion_pair)
#             fusion_page_variables = {
#                 'sample': p_args.sample
#             }
#             fusion_page = Page(fusion_pair, fusion_page_variables, 'fusion')
#             fusion = fusion_pair.split('--')

#             variations_section = Section()
#             variations_section.section_id = 'variations'
#             variations_section.title = 'Fusion gene variations'
#             variations_section.content = '''
#             Fusion gene information taken from three different sources ChiTars (NAR, 2018), 
#             tumorfusions (NAR, 2018) and Gao et al. (Cell, 2018). Genome coordinates are 
#             lifted-over GRCh37/hg19 version. <br>Note: LD (Li Ding group, RV: Roel Verhaak group, 
#             ChiTaRs fusion database).
#             '''
#             variations_section.data = db_instance.select(
#                 '''
#                 SELECT * FROM TCGA_ChiTaRS_combined_fusion_information_on_hg19
#                 WHERE h_gene = ? AND t_gene = ?''',
#                 fusion
#             )
#             fusion_page.add_section(variations_section)

#             transcripts_section = Section()
#             transcripts_section.section_id = 'transcripts'
#             transcripts_section.title = 'Ensembl transcripts'
#             transcripts_section.content = '''
#             Open reading frame (ORF) analsis of fusion genes based on Ensembl gene 
#             isoform structure.
#             '''
#             transcripts_section.data = db_instance.select(
#                 '''
#                 SELECT * FROM TCGA_ChiTaRS_combined_fusion_ORF_analyzed_gencode_h19v19
#                 WHERE h_gene = ? AND t_gene = ?''',
#                 fusion
#             )
#             fusion_page.add_section(transcripts_section)

#             ppi_section = Section()
#             ppi_section.section_id = 'ppi'
#             ppi_section.title = 'Chimeric Protein-Protein interactions'
#             ppi_section.content = '''
#             Protein-protein interactors with each fusion partner protein in wild-type.
#             Data are taken from <a href="http://chippi.md.biu.ac.il/index.html">here</a>
#             '''
#             ppi_section.data = db_instance.select(
#                 '''
#                 SELECT DISTINCT h_gene, h_gene_interactions, t_gene, t_gene_interactions
#                 FROM fusion_ppi WHERE h_gene = ? AND t_gene = ?''',
#                 fusion
#             )
#             ppi_graph = Graph(
#                 'ppi_graph',
#                 'Network graph of gene interactions',
#                 '',
#                 create_ppi_graph(ppi_section.data)
#             )
#             ppi_section.add_graph(ppi_graph)
#             fusion_page.add_section(ppi_section)

#             drugs_section = Section()
#             drugs_section.section_id = 'targeting_drugs'
#             drugs_section.title = 'Targeting drugs'
#             drugs_section.content = '''
#             Drugs targeting genes involved in this fusion gene 
#             (DrugBank Version 5.1.0 2018-04-02).
#             '''
#             drugs_section.data = db_instance.select(
#                 '''
#                 SELECT gene_symbol, drug_status, drug_bank_id, drug_name, drug_action,
#                 fusion_uniprot_related_drugs.uniprot_acc FROM fusion_uniprot_related_drugs
#                 INNER JOIN uniprot_gsymbol
#                 ON fusion_uniprot_related_drugs.uniprot_acc = uniprot_gsymbol.uniprot_acc
#                 WHERE gene_symbol = ? OR gene_symbol = ?
#                 ''',
#                 fusion
#             )
#             fusion_page.add_section(drugs_section)

#             diseases_section = Section()
#             diseases_section.section_id = 'related_diseases'
#             diseases_section.title = 'Related diseases'
#             diseases_section.content = 'Diseases associated with fusion partners (DisGeNet 4.0).'
#             diseases_section.data = db_instance.select(
#                 '''
#                 SELECT * FROM fgene_disease_associations
#                 WHERE (gene = ? OR gene = ?)
#                 AND disease_prob > 0.2001 ORDER BY disease_prob DESC''',
#                 fusion
#             )
#             fusion_page.add_section(diseases_section)
#             report.add_page(fusion_page)

#     # Index page
#     index_page_variables = {
#         'sample': p_args.sample,
#         'total_fusions': len(unknown_fusions) + len(known_fusions),
#         'known_fusions': len(known_fusions),
#         'tools': summary_file.keys()
#     }
#     index_page = Page('index', index_page_variables, 'index')

#     dashboard_section = Section()
#     dashboard_section.section_id = 'dashboard'
#     dashboard_section.title = 'Dashboard fusion summary'
#     dashboard_graph1 = Graph(
#         'tool_detection_chart',
#         'Tool detection',
#         'Displays number of found fusions per tool.',
#         create_tool_detection_chart(summary_file)
#     )
#     dashboard_graph2 = Graph(
#         'known_unknown_chart',
#         'Known Vs Unknown',
#         'Shows the ration between found and unknown missing fusions in the local database.',
#         [['known', len(known_fusions)], ['unknown', len(unknown_fusions)]])
#     dashboard_graph3 = Graph(
#         'distribution_chart',
#         'Tool detection distribution',
#         'Sum of counts detected by different tools per fusion.',
#         create_distribution_chart(summary_file))
#     dashboard_section.add_graph(dashboard_graph1)
#     dashboard_section.add_graph(dashboard_graph2)
#     dashboard_section.add_graph(dashboard_graph3)
#     index_page.add_section(dashboard_section)

#     fusion_list_section = Section()
#     fusion_list_section.section_id = 'fusion_list'
#     fusion_list_section.title = 'List of detected fusions'
#     fusion_list_section.content = '''
#         Filters fusions found by at least {tool} tools. If number of chosen tools is less 
#         than {tool} the filter is disabled. The whole list can be found in 
#         <code>results/Report-{sample}/fusions.txt</code>.
#         '''.format(tool=str(p_args.tool_num), sample=str(p_args.sample))
#     fusion_list_section.data = create_fusions_table(summary_file, known_fusions, p_args.tool_num)
#     index_page.add_section(fusion_list_section)
#     report.add_page(index_page)

def main():
    """Main function for processing command line arguments"""
    parser = argparse.ArgumentParser(
        description='Tool for generating friendly UI custom report'
    )
    parser.add_argument(
        '--ericscript',
        help='EricScript output file',
        type=str
    )
    parser.add_argument(
        '--fusioncatcher',
        help='FusionCatcher output file',
        type=str
    )
    parser.add_argument(
        '--starfusion',
        help='STAR-Fusion output file',
        type=str
    )
    parser.add_argument(
        '--pizzly',
        help='Pizzly output file',
        type=str
    )
    parser.add_argument(
        '--squid',
        help='Squid output file',
        type=str
    )
    parser.add_argument(
        '-s', '--sample',
        help='Sample name',
        type=str,
        required=True
    )
    parser.add_argument(
        '-o', '--output',
        help='Output directory',
        type=str,
        required=True
    )
    parser.add_argument(
        '-c', '--config',
        help='Input config file',
        type=str,
        required=False
    )
    parser.add_argument(
        '-t', '--tool_num',
        help='Number of tools required to detect a fusion',
        type=int,
        default=TOOL_DETECTION_CUTOFF
    )
    parser.add_argument(
        '-db', '--database',
        help='Path to database file fusions.db (for local development)',
        type=str,
        required=False
    )
    generate_report(parser.parse_args())

if __name__ == "__main__":
    main()
