# -*- coding: utf-8 -*-
import re
import ssl

import dash_bootstrap_components as dbc
import spacy
from dash import Input, Output, State, html
from dash_extensions.enrich import DashProxy, MultiplexerTransform

from new.graph_sent_merge_filter_approach import generate_question_graph_v2
from new.graph_utils import GraphUtils
from new.knowledge_graph_layout import knowledge_graph_layout
from new.question_graph_layout import question_graph_layout
from new.select_question import question_select

ssl.SSLContext.verify_mode = ssl.VerifyMode.CERT_OPTIONAL

app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()],
                external_stylesheets=[dbc.themes.BOOTSTRAP])

nlp = spacy.load("en_core_web_sm")
graph_utils = GraphUtils()
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
            , width=2)
    ], justify="center", align="around", style={"margin": "8px"}),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Subset Knowledge Graph")),
            dbc.ModalBody(knowledge_graph_layout)
        ],
        id="modal-kg",
        fullscreen=True,
    ),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Question Graph")),
            dbc.ModalBody(question_graph_layout)
        ],
        id="modal-qg",
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
                    html.Li("Export the question graph to the local filesystem")

                ]

            ),
        ],
        id="help-menu",
        title="Help Menu",
        is_open=False,
        placement="end"
    ),

], style={"height": "100vh", "overflowY": "hidden", "overflowX": "hidden"})


def get_ranked_labels(question_id, data):
    if data is None or len(data) != 1:
        return [], ''
    label = data[0]['label']
    labels = graph_utils.get_ranked_rdfs_labels(question_id, data[0]['label'])
    if label not in labels:
        labels.insert(0, {'label': label, 'value': label})
    return labels, label


def label_callback(data, value):
    regex = "<(.*)><(.*)><(.*)>"
    res = re.match(regex, value)
    if res is not None:
        gr = res.groups()
        qid = gr[0]

        no_selection = data is None or len(data) == 0
        select_disabled = data is None or len(data) != 1
        labels, label = get_ranked_labels(qid, data)
        return labels, label, select_disabled, no_selection


@app.callback(Output('select-label-dropdown', 'options'),
              Output('select-label-dropdown', 'value'),
              Output('select-label-dropdown', 'disabled'),
              Output('delete-button', 'disabled'),
              Input('question-graph', 'selectedNodeData'),
              Input('input-dropdown', 'value'))
def displaySelectedNodeData(data, value):
    return label_callback(data, value)


@app.callback(Output('select-label-dropdown', 'options'),
              Output('select-label-dropdown', 'value'),
              Output('select-label-dropdown', 'disabled'),
              Output('delete-button', 'disabled'),
              Input('question-graph', 'selectedEdgeData'),
              Input('input-dropdown', 'value')
              )
def displaySelectedEdgeData(data, value):
    return label_callback(data, value)


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
    Output("new-node-id-input", "valid"),
    Output('question-graph', 'elements'),
    Output("from-node-dropdown", "options"),
    Output("to-node-dropdown", "options"),
    Output("question-graph", "selectedNodeData"),
    Input("add-new-node-button", "n_clicks"),
    State('question-graph', 'elements'),
    State('new-node-id-input', 'value'),
    State('new-node-label-input', 'value'),
    State("from-node-dropdown", "options"),
    State("from-node-dropdown", "options")
)
def add_new_node(n_clicks, elements, new_id, new_label, from_options, to_options):
    if n_clicks > 0:

        current_ids = {ele_data['data']['id'] for ele_data in elements}

        if new_id in current_ids:
            return False, elements, from_options, to_options
        new_node = {'id': new_id, 'label': new_label}
        elements.append({'data': new_node})
        from_options.append({'value': new_id, 'label': new_label})
        to_options.append({'value': new_id, 'label': new_label})
        from_options = sorted(from_options, key=lambda d: d['label'])
        to_options = sorted(to_options, key=lambda d: d['label'])
        return True, elements, from_options, to_options, [new_node]


@app.callback(
    Output("new-edge-id-input", "valid"),
    Output('question-graph', 'elements'),
    Output("question-graph", "selectedEdgeData"),
    Input("add-new-edge-button", "n_clicks"),
    State('question-graph', 'elements'),
    State("from-node-dropdown", "value"),
    State("to-node-dropdown", "value"),
    State("new-edge-label-input", "value"),
    State("new-edge-id-input", "value")
)
def add_new_edge(n_clicks, elements, from_node_id, to_node_id, edge_label, new_id):
    if n_clicks > 0:
        current_ids = {ele_data['data']['id'] for ele_data in elements}

        if new_id in current_ids:
            return False, elements, []

        new_node = {'source': from_node_id, 'target': to_node_id, 'label': edge_label, 'id': new_id}
        elements.append({'data': new_node})
        return True, elements, [new_node]


@app.callback(
    Input('input-dropdown', 'value'),
    Output('knowledge-graph', 'elements'),
    Output('question-graph', 'elements'),
    Output('open-kg', 'disabled'),
    Output('open-qg', 'disabled'),
    Output('knowledge-graph', 'layout'),
)
def load_question_files(value):
    regex = "<(.*)><(.*)><(.*)>"
    res = re.match(regex, value)
    if res is not None:
        gr = res.groups()
        file = gr[2]
        lines = graph_utils.load_file("../resources/" + file)

        if lines <= 500:
            layout = {
                'name': 'cose-bilkent',
                'animate': False,
                'nodeRepulsion': 20000,
                'idealEdgeLength': 500,
                'nodeDimensionsIncludeLabels': True
            }
        else:
            layout = {
                'name': 'concentric',
            }

        return graph_utils.get_dash_graph(), generate_question_graph_v2(nlp(gr[1])), False, False, layout
    return None, None, True, True, None


@app.callback(
    Output("modal-kg", "is_open"),
    Input("open-kg", "n_clicks")
)
def open_kg(n_clicks):
    return n_clicks > 0


@app.callback(
    Output("modal-qg", "is_open"),
    Input("open-qg", "n_clicks")
)
def open_qg(n_clicks):
    return n_clicks > 0


@app.callback(
    Output("help-menu", "is_open"),
    Input("open-help", "n_clicks")
)
def open_qg(n_clicks):
    return n_clicks > 0


@app.callback(
    Input('export-button', 'n_clicks'),
    Output('modal-export', 'children'),
    Output('modal-export', 'is_open'),
)
def export_question_graph(n_clicks):
    if (n_clicks > 0):
        return "Question graph exported to: FILE_PATH", True


if __name__ == '__main__':
    app.run_server(debug=True)
