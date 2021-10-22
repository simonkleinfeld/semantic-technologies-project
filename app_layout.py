# -*- coding: utf-8 -*-
from dash import dcc, html, Output, Input, State
from dash_extensions.enrich import DashProxy, MultiplexerTransform

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
            dcc.Textarea(
                id='input-field',
                placeholder='Enter question',
                wrap="false",
                style={'width': 300, 'height': 25},
            ),
            html.Button('Submit', id='submit-button', n_clicks=0,
                        style={'height': 31, 'margin-left': '8px', 'vertical-align': 'top'}),

        ]),
    html.Div(
        style={
            'textAlign': 'center',
            'margin-top': 8
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


@app.callback(
    Input('submit-button', 'n_clicks'),
    Output('output-entity', 'children'),
    State('input-field', 'value')
)
def update_output_entity(n_clicks, value):
    if n_clicks > 0:
        return create_entity_content(value)


@app.callback(
    Input('submit-button', 'n_clicks'),
    Output('output-dependency', 'children'),
    State('input-field', 'value')
)
def update_output_dependency(n_clicks, value):
    if n_clicks > 0:
        return create_dependency_content(value)


@app.callback(
    Input('submit-button', 'n_clicks'),
    Output('output-knowledge', 'children'),
    State('input-field', 'value')
)
def update_output_knowledge(n_clicks, value):
    if n_clicks > 0:
        return create_knowledge_content(value)


@app.callback(
    Input('submit-button', 'n_clicks'),
    Output('output-question', 'children'),
    State('input-field', 'value')
)
def update_output_question(n_clicks, value):
    if n_clicks > 0:
        return create_question_content(value)


if __name__ == '__main__':
    app.run_server(debug=True)
