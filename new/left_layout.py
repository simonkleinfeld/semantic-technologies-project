import re
from pathlib import PurePosixPath
from urllib.parse import urlparse, unquote

import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import html

from new.graph import Graph

DIM_GENSIM = 50


def convert_uri_to_string_label(uri):
    url_path = PurePosixPath(unquote(urlparse(uri).path))
    string = url_path.name
    if type(string) != str:
        string = str(string)
    for c in ["_", "-", "#", "(", ")"]:
        if c in string:
            string = string.replace(c, " ")
    return string


def create_question_content(file):
    file1 = open(file, 'r')
    lines = file1.readlines()
    existing_nodes = set()
    lines_ = []
    regex = "<(.*)>\s<(.*)>\s<(.*)>"
    graph = Graph()
    for line in lines:
        res = re.match(regex, line)
        if res is not None:
            gr = res.groups()
            lines_.append(gr)
            subject = gr[0]
            pred = gr[1]
            obj = gr[2]
            if subject not in existing_nodes:
                s = convert_uri_to_string_label(subject)
                sl = s.split(" ")
                graph.add_node(subject, None, DIM_GENSIM, s, sl, vec=[0] * 50)
            if obj not in existing_nodes:
                s = convert_uri_to_string_label(obj)
                sl = s.split(" ")
                graph.add_node(obj, None, DIM_GENSIM, s, sl, vec=[0] * 50)
                existing_nodes.add(obj)
            p = convert_uri_to_string_label(pred)
            pl = p.split(" ")
            graph.add_edge((subject, obj), None, DIM_GENSIM, p, pl, vec=[0] * 50)
    return graph.get_dash_graph()


left_layout = html.Div([
    dbc.Row(dbc.Col(html.H5(
        children='Subset Knowledge Graph Visualization',
        style={
            'textAlign': 'center',
        }
    )), style={"margin": "8px"}),
    dbc.Row([dbc.Col(
        cyto.Cytoscape(
            id='knowledge-graph',
            elements=create_question_content("../resources/question_1.nxhd"),
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
            ]
        ), lg=10, md=12),
        dbc.Col([
            html.Header("Current Label"),
            html.Div(id="show-selected-node"),
        ],

            lg=2, md=12
        )])

])
