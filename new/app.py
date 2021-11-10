# -*- coding: utf-8 -*-
import ssl

import dash_bootstrap_components as dbc
import spacy
from dash import html, Input, Output, State
from dash_extensions.enrich import DashProxy, MultiplexerTransform

from new.left_layout import knowledge_graph_layout, get_ranked_list
from new.right_layout import question_graph_layout
from select_question import question_select

ssl.SSLContext.verify_mode = ssl.VerifyMode.CERT_OPTIONAL

app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()],
                external_stylesheets=[dbc.themes.BOOTSTRAP])

nlp = spacy.load("en_core_web_sm")

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


def label_callback(data):
    if data is None or len(data) != 1:
        return [], ''
    label = data[0]['label']
    labels = get_ranked_list(data[0]['label'])
    labels.insert(0,{'label': label, 'value': label})
    return labels, label


@app.callback(Output('select-label-dropdown', 'options'),
              Output('select-label-dropdown', 'value'),
              Output('select-label-dropdown', 'disabled'),
              Output('delete-button', 'disabled'),
              [Input('knowledge-graph', 'selectedNodeData')])
def displaySelectedNodeData(data):
    no_selection = data is None or len(data) == 0
    select_disabled = data is None or len(data) != 1
    print("select_disabled",select_disabled)
    labels, label = label_callback(data)
    return labels, label, select_disabled, no_selection


@app.callback(Output('select-label-dropdown', 'options'),
              Output('select-label-dropdown', 'value'),
              Output('select-label-dropdown', 'disabled'),
              Output('delete-button', 'disabled'),
              [Input('knowledge-graph', 'selectedEdgeData')])
def displaySelectedEdgeData(data):
    no_selection = data is None or len(data) == 0
    select_disabled = data is None or len(data) != 1
    labels, label = label_callback(data)
    return labels, label, select_disabled, no_selection


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


if __name__ == '__main__':
    app.run_server(debug=True)
