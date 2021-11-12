from dash import dcc, html

keywords_tab = dcc.Tab(label='Keywords', children=[
    html.Div(id='output-keywords', style={'margin': 8})
])


def create_keywords_content(question):
    return 'You have entered to keywords: {}'.format(question)
