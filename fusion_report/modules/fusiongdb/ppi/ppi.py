"""Protein-Protein interaction module"""
from typing import Any, Dict, List

from fusion_report.data.fusiongdb import FusionGDB
from fusion_report.modules.base_module import BaseModule


class CustomModule(BaseModule):
    """Protein-Protein interaction section in fusion page."""

    def get_data(self) -> List[Any]:
        """Gathers necessary data."""

        return FusionGDB(self.params['db_path']).select(
            '''
            SELECT DISTINCT h_gene, h_gene_interactions, t_gene, t_gene_interactions
            FROM fusion_ppi WHERE h_gene = ? AND t_gene = ?
            ''',
            self.params['fusion'].split('--')
        )

    def build_graph(self):
        """Helper function that generates Network map of Protein-Protein Interactions using
        Cytoscape.js. Additional module https://github.com/cytoscape/cytoscape.js-cose-bilkent.

        Returns:
            List structure which is defined by the Cytoscape library
        """
        data = self.get_data()
        if not data:
            return []

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

    def load(self) -> Dict[str, Any]:
        """Return module variables."""

        return {
            'data': self.build_graph(),
            'menu': ['Chimeric Protein-Protein interactions']
        }
