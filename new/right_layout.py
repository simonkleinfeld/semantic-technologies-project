import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

question_graph_layout = dbc.Row([
    dbc.Col([
            cyto.Cytoscape(
                id='question-graph',
                elements=[],
                layout={
                    'name': 'concentric'
                },
                style={
                    "width": "100%",
                    "height": "900px"
                },
                stylesheet=[
                    {'selector': 'edge', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
                    {'selector': 'node', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
                ]
            )
        ], width=600)
])
