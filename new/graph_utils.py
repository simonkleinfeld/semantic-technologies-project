import json
import re
from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse

from Levenshtein import distance
from SPARQLWrapper import SPARQLWrapper

from new.graph import Graph


class GraphUtils:
    def __init__(self):
        self.graph = Graph()
        self.DIM_GENSIM = 50
        self.sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    def convert_uri_to_string_label(self, uri):
        url_path = PurePosixPath(unquote(urlparse(uri).path))
        string = url_path.name
        if type(string) != str:
            string = str(string)
        for c in ["_", "-", "#", "(", ")", "<", ">"]:
            if c in string:
                string = string.replace(c, " ")
        return string

    def load_file(self, file):
        lines_count = 0
        file1 = open(file, 'r')
        lines = file1.readlines()
        regex = "<(.*)>\s<(.*)>\s<(.*)>"
        self.labels = set()
        self.graph = Graph()
        existing_nodes = set()
        for line in lines:
            lines_count += 1
            res = re.match(regex, line)
            if res is not None:
                gr = res.groups()
                subject = gr[0]
                pred = gr[1]
                obj = gr[2]
                if subject not in existing_nodes:
                    s = self.convert_uri_to_string_label(subject)
                    sl = s.split(" ")
                    self.graph.add_node(subject, s)
                    existing_nodes.add(subject)
                if obj not in existing_nodes:
                    s = self.convert_uri_to_string_label(obj)
                    sl = s.split(" ")
                    self.graph.add_node(obj, s)
                    existing_nodes.add(obj)
                p = self.convert_uri_to_string_label(pred)
                pl = p.split(" ")
                self.graph.add_edge((subject, obj), p)
        return lines_count

    def get_dash_graph(self):
        return self.graph.get_dash_graph()

    def get_rdfs_labels(self, question_id):
        with open('../resources/question_labels_' + str(question_id) + '.json', encoding="utf8") as json_file:
            data = json.load(json_file)
            return data['labels']

    def get_ranked_rdfs_labels(self, question_id, label):
        ranked = {}
        for rdfs_label in self.get_rdfs_labels(question_id):
            calc_distance = distance(label, rdfs_label)
            ranked[rdfs_label] = calc_distance
        sorted_labels = sorted(ranked.items(), key=lambda x: x[1], reverse=False)
        result = []
        for l, _ in sorted_labels:
            result.append({'label': l, 'value': l})
        return result
