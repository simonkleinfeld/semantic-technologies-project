import json

from dash import dcc


def load_questions():
    with open('resources/qald-6-test-multilingual.json', encoding="utf8") as json_file:
        data = json.load(json_file)
        questions = []
        for question in data["questions"]:
            for question_ in question["question"]:
                lang = question_["language"]
                q = question_["string"]
                keywords = question_["keywords"]
                value_string = "<{0}> <{1}>".format(q, keywords)
                if lang == "en":
                    questions.append({'label': q, 'value': value_string})
    return questions


question_select = dcc.Dropdown(id='input-dropdown',
                               placeholder='Select question',
                               style={'textAlign': 'center', },
                               value='',
                               clearable=False,
                               options=load_questions())
