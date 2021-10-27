import re

import dash_cytoscape as cyto
from dash import dcc, html

question_graph_tab = dcc.Tab(label='Question Graph', children=[
    html.Div(id='output-question', style={'margin': 8}, children=[
        html.Div(id='output-question-div-1', style={'margin': 8}, children=[
            html.Button('Question Tree 1', id='question-tree-button-1', style={'margin': 8}, n_clicks=0),
            html.Button('Question Tree 2', id='question-tree-button-2', style={'margin': 8}, n_clicks=0),
        ]),
        html.Div(id='output-question-div-2', style={'margin': 8, 'height': 'calc(100vh - 200px)',
                                                    'width': '100vh', }, children=[
            cyto.Cytoscape(
                id='question-graph',
                elements=[],
                layout={
                    'name': 'concentric'
                },
                style={
                    "width": "100%",
                    "height": "100%"
                },
                stylesheet=[
                    {'selector': 'edge', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
                    {'selector': 'node', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
                ]
            )
        ])
    ])
])


def create_question_content(file):
    file1 = open(file, 'r')
    lines = file1.readlines()

    existing_nodes = set()
    lines_ = []
    nodes = []
    regex = "<(.*)>\s<(.*)>\s<(.*)>"
    for line in lines:
        if (res := re.match(regex, line)) is not None:
            gr = res.groups()
            lines_.append(gr)
            subject = gr[0]
            pred = gr[1]
            obj = gr[2]
            if subject not in existing_nodes:
                nodes.append({'data': {'id': subject, 'label': subject}})
                existing_nodes.add(subject)
            if obj not in existing_nodes:
                nodes.append({'data': {'id': obj, 'label': obj}})
                existing_nodes.add(obj)
            nodes.append({'data': {'source': subject, 'target': obj, 'label': pred}})
    return nodes
