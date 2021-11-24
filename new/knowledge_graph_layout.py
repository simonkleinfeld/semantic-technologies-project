import dash_cytoscape as cyto

cyto.load_extra_layouts()

knowledge_graph_layout = cyto.Cytoscape(
    id='knowledge-graph',
    layout={
        'name': 'cose-bilkent',
        'animate': False,
        'nodeRepulsion': 20000,
        'idealEdgeLength': 500,
        'nodeDimensionsIncludeLabels': True
    },
    style={
        "width": "100%",
        "height": "calc(100vh - 150px)",
    },
    stylesheet=[
        {'selector': 'edge', 'style': {'label': 'data(label)', 'curve-style': 'haystack',
                                       'haystack-radius': 0,
                                       'width': 5,
                                       'opacity': 0.5,
                                       'line-color': '#a8eae5'}, 'text-wrap': 'wrap'},
        {'selector': 'node', 'style': {'label': 'data(label)', 'background-color': '#30c9bc'}, 'text-wrap': 'wrap'},
    ]
)
