import os

import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import dcc, html
import glob
cyto.load_extra_layouts()


def get_export_files():
    file_dir = os.path.dirname(os.path.realpath('__file__'))
    file_path = os.path.join(file_dir, '..\\output\\')
    file_path = file_path.replace("\\new\\..\\", "\\")
    export_files = []

    for file in glob.glob(file_path + "\\*.nxhd"):
        file_name = os.path.basename(file)
        export_files.append({'label': file_name, 'value': file})
    return export_files


view_export_layout = html.Div([
    dbc.Row(
        children=[
            dbc.Col(cyto.Cytoscape(
                id='view-export-graph',
                layout={
                    'name': 'cose-bilkent',
                    'animate': False,
                    'nodeRepulsion': 20000,
                    'idealEdgeLength': 500,
                    'nodeDimensionsIncludeLabels': True
                },
                style={
                    "width": "100%",
                    "height": "calc(100vh - 150px - 50px)",
                },
                stylesheet=[
                    {'selector': 'edge', 'style': {'label': 'data(label)', 'curve-style': 'haystack',
                                                   'haystack-radius': 0,
                                                   'width': 5,
                                                   'opacity': 0.5,
                                                   'line-color': '#a8eae5'}, 'text-wrap': 'wrap'},
                    {'selector': 'node', 'style': {'label': 'data(label)', 'background-color': '#30c9bc'},
                     'text-wrap': 'wrap'},
                ]
            ), width=12),
        ]
    )
])
