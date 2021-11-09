# -*- coding: utf-8 -*-

import dash_bootstrap_components as dbc
import spacy
from dash import html, Input, Output
from dash_extensions.enrich import DashProxy, MultiplexerTransform

from new.left_layout import left_layout
from new.right_layout import right_layout
from select_question import question_select

app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()],
                external_stylesheets=[dbc.themes.BOOTSTRAP])

nlp = spacy.load("en_core_web_sm")

app.title = "Question understanding interface"
app.layout = html.Div([
    dbc.Row(dbc.Col(html.H1(
        children='Question understanding interface',
        style={
            'textAlign': 'center',
        }
    )), style={"margin": "8px"}),
    dbc.Row(dbc.Col(question_select), style={"margin": "8px"}),
    dbc.Row(
        [
            dbc.Col(html.Div(
                style={
                    'padding': '8px',
                    'borderStyle': 'groove',
                    'height': '100%'
                },
                children=[left_layout]
            ), lg=6, md=12),
            dbc.Col(html.Div(
                style={
                    'padding': '8px',
                    'borderStyle': 'groove',
                    'height': '100%'
                },
                children=[right_layout]
            ), lg=6, md=12),
        ]
        , style={"margin": "16px", 'height': 'calc(100vh - 180px)'}
    )

])


@app.callback(Output('show-selected-node', 'children'),
              [Input('knowledge-graph', 'selectedNodeData')])
def displaySelectedNodeData(data):
    if data is None or len(data) != 1:
        return None
    return data[0]['label']


@app.callback(Output('show-selected-node', 'children'),
              [Input('knowledge-graph', 'selectedEdgeData')])
def displaySelectedEdgeData(data):
    if data is None or len(data) != 1:
        return None
    return data[0]['label']


@app.callback(
    Input('input-dropdown', 'value'),
    Output('question-graph-div', 'children')
)
def main_callback_select(value):
    return value


if __name__ == '__main__':
    app.run_server(debug=True)
