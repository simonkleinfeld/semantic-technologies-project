# -*- coding: utf-8 -*-
import ssl

import dash_bootstrap_components as dbc
import spacy
from dash import html, Input, Output
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
        return None
    label = data[0]['label']
    labels = get_ranked_list(data[0]['label'])
    labels.append({'label': label, 'value': label})
    return labels, label


@app.callback(Output('select-label-dropdown', 'options'),
              Output('select-label-dropdown', 'value'),
              [Input('knowledge-graph', 'selectedNodeData')])
def displaySelectedNodeData(data):
    return label_callback(data)


@app.callback(Output('select-label-dropdown', 'options'),
              Output('select-label-dropdown', 'value'),
              [Input('knowledge-graph', 'selectedEdgeData')])
def displaySelectedEdgeData(data):
    return label_callback(data)


if __name__ == '__main__':
    app.run_server(debug=True)
