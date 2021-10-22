import base64

import spacy
from dash import dcc, html
from spacy import displacy

nlp = spacy.load("en_core_web_sm")

dependency_tab = dcc.Tab(label='Dependency Tree', children=[
    html.Img(id='output-dependency', style={'margin': 8})
])


def create_dependency_content(question):
    doc = nlp(question)

    ent = displacy.render(doc, style="dep")
    ent_byts = ent.encode()
    encoded = base64.b64encode(ent_byts)
    decoded = encoded.decode()
    return_string = 'data:image/svg;base64,{}'.format(decoded)
    return return_string
