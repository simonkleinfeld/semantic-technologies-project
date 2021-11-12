import json

from dash import dcc, html


def load_questions():
    with open('../resources/questions.json', encoding="utf8") as json_file:
        data = json.load(json_file)
        questions = []
        for question in data["questions"]:
            label = question['question']
            qid = question['id']
            file = question['file']
            value = "<" + str(qid) + ">" + "<" + label + ">" + "<" + file + ">"
            questions.append({'label': label, 'value': value})
    return questions


question_select = html.Div(id='output-select-div',
                           style={'width': '100%', 'display': 'flex', 'alignItems': 'center',
                                  'justifyContent': 'center', 'margin': '8px'}, children=[
        dcc.Dropdown(id='input-dropdown',
                     placeholder='Select question',
                     style={'width': 470},
                     value='',
                     clearable=False,
                     searchable=True,
                     options=load_questions())
    ])
