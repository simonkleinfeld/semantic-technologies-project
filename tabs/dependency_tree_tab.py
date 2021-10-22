from dash import dcc, html

dependency_tab = dcc.Tab(label='Dependency Tree', children=[
    html.Div(id='output-dependency', style={'margin': 8})
])


def create_dependency_content(question):
    return 'You have entered to dependency tree: \n{}'.format(question)
