import dash_cytoscape as cyto
import spacy
from dash import dcc, html

nlp = spacy.load("en_core_web_sm")

dependency_tab = dcc.Tab(label='Dependency Tree', children=[
    html.Div(id='output-dependency-div', style={'margin': 8, 'height': 'calc(100vh - 200px)',
                                                'width': '100vh', }, children=[
        cyto.Cytoscape(
            id='output-dependency',
            elements=[],
            layout={
                'name': 'breadthfirst'
            },
            style={
              "width": "100%",
              "height": "100%"
            },
            stylesheet=[
                {'selector': 'edge', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
                {'selector': 'node', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
            ]
        )
    ])
])


def create_dependency_content(question):
    doc = nlp(question)

    nodes = []
    for token in doc:
        nodes.append({'data': {'id': token.text, 'label': '{0}'.format(token.text)}})
        for child in token.children:
            nodes.append({'data': {'source': token.text, 'target': child.text, 'label': child.dep_}})

    return nodes
