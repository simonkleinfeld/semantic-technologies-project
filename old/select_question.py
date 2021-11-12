import json

from dash import dcc, html


def load_questions():
    with open('../resources/questions.json', encoding="utf8") as json_file:
        data = json.load(json_file)
        questions = []
        for question in data["questions"]:
            questions.append({'label': question, 'value': question})
    return questions


question_select = html.Div(id='output-select-div',
                           style={'width': '100%', 'display': 'flex', 'align-items': 'center',
                                  'justify-content': 'center'}, children=[

        dcc.Dropdown(id='input-dropdown',
                     placeholder='Select question',
                     style={'width': 470},
                     value='',
                     clearable=False,
                     searchable=True,
                     options=load_questions())
    ])
