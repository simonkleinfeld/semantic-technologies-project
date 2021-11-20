import dash_bootstrap_components as dbc
import dash_cytoscape as cyto


knowledge_graph_layout = dbc.Row([
    dbc.Col(
        [
            dbc.Col(
                cyto.Cytoscape(
                    id='knowledge-graph',
                    layout={
                        'name': 'random'
                    },
                    style={
                        "width": "100%",
                        "height": "600px"
                    },
                    stylesheet=[
                        {'selector': 'edge', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
                        {'selector': 'node', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
                    ],
                ), width=12)

        ],

        width=12)
])
