# -*- coding: utf-8 -*-
import json

import spacy
from dash import dcc, html, Output, Input, State
from dash_extensions.enrich import DashProxy, MultiplexerTransform

from select_question import question_select
from tabs.dependency_tree_tab import dependency_tab, create_dependency_content
from tabs.entity_names_tab import entity_tab, create_entity_content
from tabs.keywords_tab import keywords_tab, create_keywords_content
from tabs.knowledge_graph_tab import knowledge_graph_tab, create_knowledge_content
from tabs.question_graph_tab import question_graph_tab, create_question_content

app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()])

nlp = spacy.load("en_core_web_sm")

app.title = "Question understanding interface"
app.layout = html.Div([
    html.H1(
        children='Question understanding interface',
        style={
            'textAlign': 'center',
        }
    ),
    html.Div(
        style={
            'textAlign': 'center',
        },
        children=
        [
            question_select,
            dcc.Textarea(
                id='input-field',
                placeholder='Enter question',
                wrap="false",
                style={'width': 300, 'height': 25, 'margin': 8},
            ),
            html.Button('Submit', id='submit-button', n_clicks=0,
                        style={'height': 31, 'margin': '8px', 'verticalAlign': 'top'}, disabled=True),
            html.Button('Add to list', id='add-button', n_clicks=0,
                        style={'height': 31, 'margin': '8px', 'verticalAlign': 'top'}, disabled=True)
        ]),
    html.Div(
        style={
            'textAlign': 'center',
        },
        children=[
            dcc.Tabs(
                children=[
                    entity_tab,
                    dependency_tab,
                    keywords_tab,
                    question_graph_tab,
                    knowledge_graph_tab
                ]

            )

        ]
    )

])


@app.callback(
    Input('input-field', 'value'),
    Output('submit-button', 'disabled'),
    Output('add-button', 'disabled'),
)
def enable_disable_button(input_value):
    disabled = len(input_value) == 0
    return disabled, disabled


@app.callback(
    Input('question-tree-button-1', 'n_clicks'),
    Output('question-graph', 'elements'),
)
def update_output_question(n_clicks):
    if n_clicks > 0:
        return create_question_content("resources/question_1.nxhd")


@app.callback(
    Input('question-tree-button-2', 'n_clicks'),
    Output('question-graph', 'elements'),
)
def update_output_question(n_clicks):
    if n_clicks > 0:
        return create_question_content("resources/question_2.nxhd")


def create_outputs(question):
    doc = nlp(question)

    return create_entity_content(doc), \
           create_dependency_content(doc), \
           create_keywords_content(question), \
           create_knowledge_content(question)


@app.callback(
    Input('submit-button', 'n_clicks'),
    Output('output-entity', 'data'),
    Output('output-dependency', 'elements'),
    Output('output-keywords', 'children'),
    Output('output-knowledge', 'children'),
    State('input-field', 'value')
)
def main_callback_submit(n_clicks, value):
    if n_clicks > 0:
        return create_outputs(value)


@app.callback(
    Input('input-dropdown', 'value'),
    Output('output-entity', 'data'),
    Output('output-dependency', 'elements'),
    Output('output-keywords', 'children'),
    Output('output-knowledge', 'children'),
)
def main_callback_select(value):
    return create_outputs(value)


@app.callback(
    Input('add-button', 'n_clicks'),
    Output('input-dropdown', 'options'),
    Output('input-dropdown', 'value'),
    State('input-field', 'value'),
    State('input-dropdown', 'options')
)
def update_output_knowledge(n_clicks, value, options):
    if n_clicks > 0:
        options.append({'label': value, 'value': value})
        questions = []
        for option in options:
            questions.append(option['value'])
        data = {'questions': questions}
        with open('resources/questions.json', 'w', encoding='utf8') as outfile:
            json.dump(data, outfile)
        return options, value


if __name__ == '__main__':
    app.run_server(debug=True)
