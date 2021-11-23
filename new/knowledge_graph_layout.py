import dash_cytoscape as cyto

knowledge_graph_layout = cyto.Cytoscape(
    id='knowledge-graph',
    layout={
        'name': 'concentric'
    },
    style={
        "width": "100%",
        "height": "calc(100vh - 150px)",
    },
    stylesheet=[
        {'selector': 'edge', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
        {'selector': 'node', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
    ]
)
