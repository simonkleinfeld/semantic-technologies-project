# -*- coding: utf-8 -*-
import re

from dash import dcc, html, Output, Input
from dash_extensions.enrich import DashProxy, MultiplexerTransform

from select_question import question_select
from tabs.dependency_tree_tab import dependency_tab, create_dependency_content
from tabs.entity_names_tab import entity_tab, create_entity_content
from tabs.knowledge_graph_tab import knowledge_graph_tab, create_knowledge_content
from tabs.question_graph_tab import question_graph_tab, create_question_content

app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()])

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
            question_select
        ]),
    html.Div(
        style={
            'textAlign': 'center',
            'marginTop': 8
        },
        children=[
            dcc.Tabs(
                children=[
                    entity_tab,
                    dependency_tab,
                    question_graph_tab,
                    knowledge_graph_tab
                ]

            )

        ]
    )

])


def get_label_and_keywords(question):
    print('question', question)
    regex = "<(.*)>\s<(.*)>"
    if (res := re.match(regex, question)) is not None:
        gr = res.groups()
        question = gr[0]
        keywords = gr[1]
        return question, keywords


@app.callback(
    Input('input-dropdown', 'value'),
    Output('output-entity', 'data'),
)
def update_output_entity(value):
    label, _ = get_label_and_keywords(value)
    return create_entity_content(label)


@app.callback(
    Input('input-dropdown', 'value'),
    Output('output-dependency', 'elements'),
)
def update_output_dependency(value):
    label, _ = get_label_and_keywords(value)
    return create_dependency_content(label)


@app.callback(
    Input('input-dropdown', 'value'),
    Output('output-knowledge', 'children'),
)
def update_output_knowledge(value):
    label, keywords = get_label_and_keywords(value)
    return create_knowledge_content(label, keywords)


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


if __name__ == '__main__':
    app.run_server(debug=True)
