import spacy
from dash import dcc, html, dash_table

nlp = spacy.load("en_core_web_sm")
columns = ["Text", "Start", "End", "Label"]
entity_tab = dcc.Tab(label='Entity Names', children=[
    html.Div(id='output-entity-div', style={'margin': 8}, children=[

        dash_table.DataTable(id='output-entity', columns=[{'name': i, 'id': i} for i in columns])
    ])
])


def create_entity_content(question):
    doc = nlp(question)

    res = []
    for e in doc.ents:
        res.append({
            "Text": e.text,
            "Start": e.start_char,
            "End": e.end_char,
            "Label": e.label_
        })
    return res
