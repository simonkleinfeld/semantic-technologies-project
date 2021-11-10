import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import dcc, html

from new.graph_utils import GraphUtils

graph_utils = GraphUtils()
graph_utils.load_file("../resources/question_1.nxhd")
graph_utils.get_rdfs_labels()

knowledge_graph_layout = dbc.Row([
    dbc.Col(
        [
            dbc.Nav([
                dcc.Dropdown(id='select-label-dropdown',
                             placeholder='Select new label',
                             clearable=False,
                             searchable=True,
                             style={'width': 300},
                             disabled=True
                             ),
                html.Button('Delete', id='delete-button', n_clicks=0, disabled=True),
            ]
            ),
            dbc.Col(
                cyto.Cytoscape(
                    id='knowledge-graph',
                    elements=graph_utils.get_dash_graph(),
                    layout={
                        'name': 'concentric'
                    },
                    style={
                        "width": "100%",
                        "height": "600px"
                    },
                    stylesheet=[
                        {'selector': 'edge', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
                        {'selector': 'node', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
                    ],
                ), width=12)

        ],

        width=12)
])


def get_ranked_list(selected_label):
    ranked = graph_utils.get_ranked_rdfs_labels(selected_label)
    return ranked
