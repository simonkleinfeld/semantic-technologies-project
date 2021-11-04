# -*- coding: utf-8 -*-
import json
import random
import pandas as pd
import spacy

import dash_core_components as dcc
import dash_cytoscape as cyto
import dash_html_components as html
from dash.dependencies import State
from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform
from dash import dash_table

from tabs.question_graph_tab import create_question_content

app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()])

styles = {
    'json-output': {
        'overflow-y': 'scroll',
        'height': 'calc(50% - 25px)',
        'border': 'thin lightgrey solid'
    },
    'tab': {'height': 'calc(98vh - 115px)'}
}

app.layout = html.Div([
    dcc.Store(id='graph_struct'),
    dcc.Store(id='text_input'),
    html.Div(className='eight columns', children=[
        cyto.Cytoscape(
            id='cytoscape',
            elements=create_question_content("resources/question_2.nxhd"),
            layout={
                'name': 'concentric'
            },
            style={
                'height': '95vh',
                'width': '100%'
            },
            stylesheet=[
                {'selector': 'edge', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
                {'selector': 'node', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
            ]
        )
    ]),

    html.Div(className='four columns', children=[
        dcc.Tabs(id='tabs', children=[
            dcc.Tab(label='Actions', children=[
                html.Button("Remove Selected Nodes", id='remove_button'),
                dcc.Input(id='input_text', type='text', value='Here could be your question'),
                html.Button('Submit', id='submit_button'),

                html.H1(id='keywords_table'),

            ]),
            dcc.Tab(label='Selected Data', children=[
                html.Div(style=styles['tab'], children=[
                    html.P('Node Data JSON:'),
                    html.Pre(
                        id='selected_node_data_json_output',
                        style=styles['json-output']
                    ),
                    html.P('Edge Data JSON:'),
                    html.Pre(
                        id='selected_edge_data_json_output',
                        style=styles['json-output']
                    )
                ])
            ]),
        ]),

    ])
])


@app.callback([
    Output('cytoscape', 'elements'),
    Output('keywords_table', 'children')], 
    [Input('submit_button', 'n_clicks')],
    [State('input_text', 'value')])
def init_graph_with_data(_, value):

    # keyword detection
    col = [
        {'name': 'Text', 'id': 'Text'},
        {'name': 'Root.text', 'id': 'Root.text'},
        {'name': 'Root.dependency', 'id': 'Root.dependency'},
        {'name': 'Root.head.text', 'id': 'Root.head.text'},
    ]

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(value)

    data = []

    doc = nlp(value)
    for chunk in doc.noun_chunks:
        data.append({   'Text': chunk.text, 
                        'Root.text': chunk.root.text, 
                        'Root.dependency': chunk.root.dep_,
                        'Root.head.text': chunk.root.head.text,
                    })

    # graph creation
    nodes = [
        {'data': {'id': str(i), 'label': 'Node {}'.format(i)}}
        for i in range(1, 21)
    ]

    edges = [
        {'data': {'source': str(random.randint(1, 20)), 'target': str(random.randint(1, 20))}}
        for _ in range(30)
    ]

    return nodes + edges, dash_table.DataTable(data=data, columns=col)

    


@app.callback(Output('cytoscape', 'elements'),
              [Input('remove_button', 'n_clicks')],
              [State('cytoscape', 'elements'),
               State('cytoscape', 'selectedNodeData')])
def remove_selected_nodes(_, elements, data):
    if elements and data:
        ids_to_remove = {ele_data['id'] for ele_data in data}
        print("Before:", elements)
        new_elements = [ele for ele in elements if ele['data']['id'] not in ids_to_remove]
        print("After:", new_elements)
        return new_elements

    return elements


@app.callback(Output('selected_node_data_json_output', 'children'),
              [Input('cytoscape', 'selectedNodeData')])
def displaySelectedNodeData(data):
    return json.dumps(data, indent=2)


@app.callback(Output('selected_edge_data_json_output', 'children'),
              [Input('cytoscape', 'selectedEdgeData')])
def displaySelectedEdgeData(data):
    return json.dumps(data, indent=2)


if __name__ == '__main__':
    app.run_server(debug=True)
