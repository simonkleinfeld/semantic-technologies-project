# -*- coding: utf-8 -*-
import copy
import os
import re
import ssl
import time
from copy import deepcopy
from pathlib import Path

import dash_bootstrap_components as dbc
import spacy
from dash import Input, Output, State, html
from dash_extensions.enrich import DashProxy, MultiplexerTransform

from layout.graph_sent_merge_filter_approach import generate_question_graph_v2, export_qg_with_kg_annotations
from layout.graph_utils import GraphUtils
from layout.knowledge_graph_layout import knowledge_graph_layout
from layout.question_graph_layout import question_graph_layout
from layout.select_question import question_select
from layout.view_export_layout import view_export_layout
from os import path
ssl.SSLContext.verify_mode = ssl.VerifyMode.CERT_OPTIONAL

app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()],
                external_stylesheets=[dbc.themes.BOOTSTRAP])

graph_id_ = ""
graph_triplets_ = ""
graph_ = None

nlp = spacy.load("en_core_web_sm")
graph_utils = GraphUtils()
graph_utils_export = GraphUtils()
app.title = "Question understanding interface"
app.layout = html.Div([
    dbc.Row(
        dbc.Col(html.H1(
            children='Question understanding interface',
            style={
                'textAlign': 'center',
            }
        ), width=6), justify="center", align="center", style={"margin": "8px", "paddingTop": "18%"}),
    dbc.Row(
        dbc.Col(html.Header(
            "Select a question below and have a look on the knowledge graph or the generated question graph",
            style={
                'textAlign': 'center',
            }
        )), justify="center", align="center", style={"margin": "8px"}),
    dbc.Row([
        dbc.Col(question_select, width=4),
        dbc.Col(dbc.Button("?", id="open-help", n_clicks=0), width=1)],
        justify="center",
        align="center", style={"margin": "8px"}),
    dbc.Row([
        dbc.Col(
            dbc.Button("Open knowledge graph", id="open-kg", n_clicks=0, disabled=True),
            width=2),
        dbc.Col(
            dbc.Button("Open question graph", id="open-qg", n_clicks=0, disabled=True)
            , width=2),
        dbc.Col(
            dbc.Button("View export", id="open-view-export", n_clicks=0, disabled=True)
            , width=2)
    ], justify="center", align="around", style={"margin": "8px"}),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Subset Knowledge Graph")),
            dbc.ModalBody(knowledge_graph_layout),
            dbc.ModalFooter(children=[html.Div(
                "For graphs with more than 500 nodes, only a subset of the nodes is displayed. "
                "The number can be adjusted via the selection list above the graph. "
                "A large number of nodes results in massive performance losses.")])
        ],
        id="modal-kg",
        fullscreen=True,
    ),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Question Graph")),
            dbc.ModalBody(question_graph_layout),
            dbc.ModalFooter(id="question-graph-footer")
        ],
        id="modal-qg",
        fullscreen=True,
    ),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("View Export")),
            dbc.ModalBody(view_export_layout),
            dbc.ModalFooter(
                "Select an export with the select item above")
        ],
        id="modal-export",
        fullscreen=True,
    ),
    dbc.Offcanvas(
        children=[
            html.P("Welcome to the question understanding interface, following features are currently supported"),
            html.Ol(
                [
                    html.Li("Selection of a fixed sized set of questions"),
                    html.Li("Visualizing a subset of a knowledge graph, corresponding to the question"),
                    html.Li("Generating a question graph for this question"),
                    html.Li("Editing the generated question graph"),
                    html.Li("Export the question graph to the local filesystem"),
                    html.Li("The exported question graph can be displayed using the view export button"),
                ]

            ),
        ],
        id="help-menu",
        title="Help Menu",
        is_open=False,
        placement="end"
    ),

], style={"height": "100vh", "overflowY": "hidden", "overflowX": "hidden"})


def get_ranked_labels(question_id, data, node):
    if data is None or len(data) != 1:
        return [], ''
    label = data[0]['label']
    labels = graph_utils.get_ranked_rdfs_labels(question_id, data[0]['label'], node)
    if label not in labels:
        labels.insert(0, {'label': label, 'value': label})
    return labels, label


def label_callback(data, value, node):
    regex = "<(.*)><(.*)><(.*)>"
    res = re.match(regex, value)
    if res is not None:
        gr = res.groups()
        qid = gr[0]
        no_selection = data is None or len(data) == 0
        select_disabled = data is None or len(data) != 1
        labels, label = get_ranked_labels(qid, data, node)
        return labels, label, select_disabled, no_selection


@app.callback(Output('select-label-dropdown', 'options'),
              Output('select-label-dropdown', 'value'),
              Output('select-label-dropdown', 'disabled'),
              Output('delete-button', 'disabled'),
              Input('question-graph', 'selectedNodeData'),
              Input('input-dropdown', 'value'))
def display_selected_node_data(data, value):
    return label_callback(data, value, True)


@app.callback(Output('select-label-dropdown', 'options'),
              Output('select-label-dropdown', 'value'),
              Output('select-label-dropdown', 'disabled'),
              Output('delete-button', 'disabled'),
              Input('question-graph', 'selectedEdgeData'),
              Input('input-dropdown', 'value')
              )
def display_selected_edge_data(data, value):
    return label_callback(data, value, False)


@app.callback(Output('selected-node-id', 'children'),
              Input('knowledge-graph', 'selectedEdgeData'))
def show_edge_id(selected_edge):
    if selected_edge is not None and len(selected_edge) == 1:
        return selected_edge[0]["uri"]
    return ""


@app.callback(Output('selected-node-id', 'children'),
              Input('knowledge-graph', 'selectedNodeData'))
def show_node_id(selected_node):
    if selected_node is not None and len(selected_node) == 1:
        return selected_node[0]["id"]
    return ""


@app.callback(
    Output('question-graph', 'elements'),
    Input('delete-button', 'n_clicks'),
    State('question-graph', 'selectedEdgeData'),
    State('question-graph', 'selectedNodeData'),
    State('question-graph', 'elements'),
)
def delete_nodes_edges(n_clicks, edges, nodes, elements):
    if n_clicks <= 0:
        return elements
    if edges is None:
        edges = []
    if nodes is None:
        nodes = []
    elements_to_remove = edges + nodes
    ids_to_remove = {ele_data['id'] for ele_data in elements_to_remove}
    new_elements = [ele for ele in elements if ele['data']['id'] not in ids_to_remove]
    return new_elements


@app.callback(
    Output('question-graph', 'elements'),
    Input('select-label-dropdown', 'value'),
    State('question-graph', 'selectedEdgeData'),
    State('question-graph', 'selectedNodeData'),
    State('question-graph', 'elements'),
)
def delete_nodes_edges(value, edges, nodes, elements):
    if value is None:
        return elements
    if edges is None:
        edges = []
    if nodes is None:
        nodes = []
    elements_to_change = edges + nodes
    if len(elements_to_change) != 1:
        return elements
    id_to_change = elements_to_change[0]['id']
    for element in elements:
        if element['data']['id'] == id_to_change:
            element['data']['label'] = value
            break
    return elements


def create_node_menu_items(elements):
    menu_list = []
    for element in elements:
        data = element['data']
        if 'target' not in data:
            label = data['label']
            id_ = data['id']
            menu_list.append({'label': label, 'value': id_})
    menu_list = sorted(menu_list, key=lambda d: d['label'])
    return menu_list


@app.callback(
    Output("modal-add-dialog", "is_open"),
    Output("from-node-dropdown", "options"),
    Output("to-node-dropdown", "options"),
    Input("add-button", "n_clicks"),
    State('question-graph', 'elements')
)
def toggle_modal(n_clicks, elements):
    menu_list = create_node_menu_items(elements)

    return n_clicks > 0, menu_list, menu_list


@app.callback(
    Output('question-graph', 'elements'),
    Output("from-node-dropdown", "options"),
    Output("to-node-dropdown", "options"),
    Output("question-graph", "selectedNodeData"),
    Input("add-new-node-button", "n_clicks"),
    State('question-graph', 'elements'),
    State('new-node-label-input', 'value'),
    State("from-node-dropdown", "options"),
    State("from-node-dropdown", "options")
)
def add_new_node(n_clicks, elements, new_label, from_options, to_options):
    if n_clicks > 0:

        new_id = time.time()
        new_node = {'id': new_id, 'label': new_label}
        elements.append({'data': new_node})
        from_options.append({'value': new_id, 'label': new_label})
        to_options.append({'value': new_id, 'label': new_label})
        from_options = sorted(from_options, key=lambda d: d['label'])
        to_options = sorted(to_options, key=lambda d: d['label'])
        return elements, from_options, to_options, [new_node]


@app.callback(
    Output('question-graph', 'elements'),
    Output("question-graph", "selectedEdgeData"),
    Input("add-new-edge-button", "n_clicks"),
    State('question-graph', 'elements'),
    State("from-node-dropdown", "value"),
    State("to-node-dropdown", "value"),
    State("new-edge-label-input", "value"),
)
def add_new_edge(n_clicks, elements, from_node_id, to_node_id, edge_label):
    if n_clicks > 0:
        new_id = time.time()
        new_node = {'source': from_node_id, 'target': to_node_id, 'label': edge_label, 'id': new_id}
        elements.append({'data': new_node})
        return  elements, [new_node]


# select-nr-of-nodes style
# displayed nodes
# list for select item
def calculate_nr_of_nodes(all_nodes):
    nodes_to_display = all_nodes
    steps = 50
    if all_nodes <= 500:
        return {'width': 300, 'display': 'none'}, nodes_to_display, []
    if all_nodes > 1000:
        steps = 100
    if all_nodes > 2000:
        steps = 150
    current_nr = 0
    nodes_list = []
    while current_nr < all_nodes:
        nodes_list.append({'label': current_nr, 'value': current_nr})
        if current_nr <= 500:
            nodes_to_display = current_nr
        current_nr += steps

    nodes_list.append({'label': all_nodes, 'value': all_nodes})

    return {'width': 300, 'display': 'inherit'}, nodes_to_display, nodes_list


@app.callback(
    Input('input-dropdown', 'value'),
    Output('knowledge-graph', 'elements'),
    Output('knowledge-graph-fallback', 'elements'),
    Output('knowledge-graph', 'style'),
    Output('knowledge-graph-fallback', 'style'),
    Output('question-graph', 'elements'),
    Output('open-kg', 'disabled'),
    Output('open-qg', 'disabled'),
    Output('open-view-export', 'disabled'),
    Output('select-nr-of-nodes', 'style'),
    Output('select-nr-of-nodes', 'value'),
    Output('select-nr-of-nodes', 'options'),
)
def load_question_files(value):
    global graph_triplets_
    global graph_id_
    global graph_
    regex = "<(.*)><(.*)><(.*)>"
    res = re.match(regex, value)
    if res is not None:
        gr = res.groups()
        file = gr[2]
        nr_of_edges, graph_triplets_ = graph_utils.load_file("../resources/" + file)
        graph_id_ = gr[0]
        graph_ = copy.deepcopy(generate_question_graph_v2(nlp(gr[1])))
        gra = copy.deepcopy(graph_)
        nodes_select_enabled, nodes_to_display, nodes_list = calculate_nr_of_nodes(nr_of_edges)

        style = {
            "width": "100%",
            "height": "calc(100vh - 150px - 50px)",
        }
        normal_style = dict(style)
        fallback_style = dict(style)
        if nr_of_edges > 500:
            normal_style['display'] = 'none'
        else:
            fallback_style['display'] = 'none'

        knowledge_graph = graph_utils.get_dash_graph(nodes_to_display)
        print(len(graph_))
        parent_dir = Path(os.getcwd()).parent
        export_path = os.path.join(parent_dir, 'output', "qg_output_{}.nxhd".format(graph_id_))
        is_path = path.isfile(export_path)
        return knowledge_graph, knowledge_graph, normal_style, fallback_style, gra, \
               False, False, not is_path, nodes_select_enabled, nodes_to_display, nodes_list


@app.callback(
    Input('select-nr-of-nodes', 'value'),
    State('knowledge-graph', 'elements'),
    Output('knowledge-graph', 'elements'),
    Output('knowledge-graph-fallback', 'elements'),
)
def load_question_files_with_more_nodes(nr_of_nodes, knowledge_graph_elements):
    if knowledge_graph_elements is not None:
        nodes = graph_utils.get_dash_graph(nr_of_nodes)
        return nodes, nodes
    return knowledge_graph_elements, knowledge_graph_elements


@app.callback(
    Output("modal-kg", "is_open"),
    Input("open-kg", "n_clicks")
)
def open_kg(n_clicks):
    return n_clicks > 0


@app.callback(
    Output("modal-export", "is_open"),
    Input("open-view-export", "n_clicks")
)
def open_export(n_clicks):
    return n_clicks > 0


@app.callback(
    Output("modal-qg", "is_open"),
    Output("question-graph-footer", "children"),
    Input("open-qg", "n_clicks")
)
def open_qg(n_clicks):
    return n_clicks > 0, ""


@app.callback(
    Output("help-menu", "is_open"),
    Input("open-help", "n_clicks")
)
def open_qg(n_clicks):
    return n_clicks > 0


@app.callback(
    Output("view-export-graph", "elements"),
    Input("open-view-export", "n_clicks"),
)
def generate_export_graph(n_clicks):
    if n_clicks > 0:
        global graph_id_
        export_path = os.path.join(Path(os.getcwd()).parent, 'output', "qg_output_{}.nxhd".format(graph_id_))
        edges, _ = graph_utils_export.load_file(export_path)
        return graph_utils_export.get_dash_graph(edges)


@app.callback(
    Input('export-button', 'n_clicks'),
    Output('question-graph-footer', 'children'),
    Output('open-view-export', 'disabled'),
)
def export_question_graph(n_clicks):
    global graph_triplets_
    global graph_id_
    global graph_
    if n_clicks > 0:
        if graph_id_ is not None and graph_triplets_ is not None and graph_ is not None:
            res, triple_number = export_qg_with_kg_annotations(graph_, graph_triplets_, graph_id_)
            return "Question graph exported to: {} with {} triples".format(res, triple_number), False
        return "Something went wrong", True


if __name__ == '__main__':
    app.run_server(debug=True)
