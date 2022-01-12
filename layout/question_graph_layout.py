import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import dcc, html

question_graph_layout = html.Div([
    dbc.Row(
        dbc.Col(
            dbc.Nav([
                dcc.Dropdown(id='select-label-dropdown',
                             placeholder='Select new label',
                             clearable=False,
                             searchable=True,
                             style={'width': 300},
                             disabled=True
                             ),
                html.Button('Delete', id='delete-button', n_clicks=0, disabled=True),
                html.Button('Add nodes/edges', id='add-button', n_clicks=0, disabled=False),
                html.Button('Export', id='export-button', n_clicks=0, disabled=False),
            ]))),
    dbc.Row(
        children=[
            dbc.Col(cyto.Cytoscape(
                id='question-graph',
                elements=[],
                layout={
                    'name': 'cose-bilkent',
                    'animate': False,
                    'nodeRepulsion': 2000,
                    'idealEdgeLength': 50,
                    'nodeDimensionsIncludeLabels': True
                },
                style={
                    "width": "100%",
                    "height": "calc(100vh - 210px)",
                },
                stylesheet=[
                    {'selector': 'edge', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
                    {'selector': 'node', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
                ]
            ), width=12)
        ],
    ),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Add nodes and egdes"), close_button=True),
            dbc.ModalBody([
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("Label"),
                        dbc.Input(placeholder="Label", id="new-node-label-input"),
                        dbc.Button("Add node", id="add-new-node-button", n_clicks=0)
                    ],
                    className="mb-3",
                ),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("From"),
                        dcc.Dropdown(id='from-node-dropdown',
                                     placeholder='Node',
                                     value='',
                                     style={'width': 200},
                                     clearable=False,
                                     searchable=True,
                                     options=[]),
                        dbc.InputGroupText("To"),
                        dcc.Dropdown(id='to-node-dropdown',
                                     placeholder='Node',
                                     value='',
                                     style={'width': 200},
                                     clearable=False,
                                     searchable=True,
                                     options=[]),

                    ],
                    className="mb-3",
                ),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("Label"),
                        dbc.Input(placeholder="Label", id="new-edge-label-input"),
                        dbc.Button("Add edge", id="add-new-edge-button", n_clicks=0)
                    ],
                    className="mb-3",
                )

            ])

        ],
        id="modal-add-dialog",
        centered=True,
        is_open=False,
        size='lg'
    )

])
