import dash_bootstrap_components as dbc
from dash import html

right_layout = html.Div([
    dbc.Row(dbc.Col(html.H5(
        children='Question Graph Visualization',
        style={
            'textAlign': 'center',
        }
    )), style={"margin": "8px"}),
    dbc.Row(dbc.Col(
        html.Div(id='question-graph-div',
                 style={
                 }, )

    ))

])
