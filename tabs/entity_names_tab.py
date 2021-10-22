from dash import dcc, html

entity_tab = dcc.Tab(label='Entity Names', children=[
    html.Div(id='output-entity', style={'margin': 8})
])


def create_entity_content(question):
    return 'You have entered to entity: \n{}'.format(question)
