# -*- coding: utf-8 -*-
import re
import ssl

import dash_bootstrap_components as dbc
import spacy
from dash import html, Input, Output, State
from dash_extensions.enrich import DashProxy, MultiplexerTransform

from new.graph_utils import GraphUtils
from new.left_layout import knowledge_graph_layout
from new.right_layout import question_graph_layout
from select_question import question_select

ssl.SSLContext.verify_mode = ssl.VerifyMode.CERT_OPTIONAL

app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()],
                external_stylesheets=[dbc.themes.BOOTSTRAP])

nlp = spacy.load("en_core_web_sm")
graph_utils = GraphUtils()
app.title = "Question understanding interface"
app.layout = html.Div([
    dbc.Row([
        dbc.Col(html.H1(
            children='Question understanding interface',
            style={
                'textAlign': 'center',
            }
        )),
        dbc.Col(
            html.Header(
                "Please select a question in the select below. "
                "Then the subset of the knowledge graph and a generated question graph are displayed below",
                style={
                    'textAlign': 'center',
                }
            ),
            width=12),
        dbc.Col(question_select, width=12),
    ]),
    dbc.Row(
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        knowledge_graph_layout
                    ],
                    title="Subset Knowledge Graph Visualization",
                ),
                dbc.AccordionItem(
                    [
                        question_graph_layout
                    ],
                    title="Question Graph Visualization",
                )
            ]

        ))

])


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
              Input('knowledge-graph', 'selectedNodeData'),
              Input('input-dropdown', 'value'))
def displaySelectedNodeData(data, value):
    return label_callback(data, value)


@app.callback(Output('select-label-dropdown', 'options'),
              Output('select-label-dropdown', 'value'),
              Output('select-label-dropdown', 'disabled'),
              Output('delete-button', 'disabled'),
              Input('knowledge-graph', 'selectedEdgeData'),
              Input('input-dropdown', 'value')
              )
def displaySelectedEdgeData(data, value):
    return label_callback(data, value)


@app.callback(
    Output('knowledge-graph', 'elements'),
    Input('delete-button', 'n_clicks'),
    State('knowledge-graph', 'selectedEdgeData'),
    State('knowledge-graph', 'selectedNodeData'),
    State('knowledge-graph', 'elements'),
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
    Output('knowledge-graph', 'elements'),
    Input('select-label-dropdown', 'value'),
    State('knowledge-graph', 'selectedEdgeData'),
    State('knowledge-graph', 'selectedNodeData'),
    State('knowledge-graph', 'elements'),
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
    State('knowledge-graph', 'elements')
)
def toggle_modal(n_clicks, elements):
    menu_list = create_node_menu_items(elements)

    return n_clicks > 0, menu_list, menu_list


@app.callback(
    Output("new-node-id-input", "valid"),
    Output('knowledge-graph', 'elements'),
    Output("from-node-dropdown", "options"),
    Output("to-node-dropdown", "options"),
    Output("knowledge-graph", "selectedNodeData"),
    Input("add-new-node-button", "n_clicks"),
    State('knowledge-graph', 'elements'),
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
    Output('knowledge-graph', 'elements'),
    Output("knowledge-graph", "selectedEdgeData"),
    Input("add-new-edge-button", "n_clicks"),
    State('knowledge-graph', 'elements'),
    State("from-node-dropdown", "value"),
    State("from-node-dropdown", "value"),
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
)
def load_question_files(value):
    regex = "<(.*)><(.*)><(.*)>"
    res = re.match(regex, value)
    if res is not None:
        gr = res.groups()
        file = gr[2]
        graph_utils.load_file("../resources/" + file)
        return graph_utils.get_dash_graph()


if __name__ == '__main__':
    app.run_server(debug=True)
