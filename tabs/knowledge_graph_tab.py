from dash import dcc, html

knowledge_graph_tab = dcc.Tab(label='Knowledge Graph', children=[
    html.Div(id='output-knowledge', style={'margin': 8})
])


def create_knowledge_content(question):
    return 'You have entered to knowledge graph: {}'.format(question)
