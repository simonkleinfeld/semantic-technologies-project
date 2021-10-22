from dash import dcc, html

question_graph_tab = dcc.Tab(label='Question Graph', children=[
    html.Div(id='output-question', style={'margin': 8})
])


def create_question_content(question):
    return 'You have entered to question graph: \n{}'.format(question)
