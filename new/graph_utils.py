import re
from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse

from Levenshtein import distance
from SPARQLWrapper import SPARQLWrapper, JSON

from new.graph import Graph


class GraphUtils:
    def __init__(self):
        self.graph = Graph()
        self.DIM_GENSIM = 50
        self.uris = set()
        self.labels = set()
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
        file1 = open(file, 'r')
        lines = file1.readlines()
        regex = "(<.*>)\s(<.*>)\s(<.*>)"
        self.labels = set()
        self.graph = Graph()
        existing_nodes = set()
        for line in lines:
            res = re.match(regex, line)
            if res is not None:
                gr = res.groups()
                subject = gr[0]
                pred = gr[1]
                obj = gr[2]
                if subject not in existing_nodes:
                    s = self.convert_uri_to_string_label(subject)
                    sl = s.split(" ")
                    self.graph.add_node(subject, None, self.DIM_GENSIM, s, sl, vec=[0] * 50)
                    existing_nodes.add(subject)
                if obj not in existing_nodes:
                    s = self.convert_uri_to_string_label(obj)
                    sl = s.split(" ")
                    self.graph.add_node(obj, None, self.DIM_GENSIM, s, sl, vec=[0] * 50)
                    existing_nodes.add(obj)
                p = self.convert_uri_to_string_label(pred)
                pl = p.split(" ")
                self.graph.add_edge((subject, obj), None, self.DIM_GENSIM, p, pl, vec=[0] * 50)
                if subject.startswith("<http://dbpedia.org/"):
                    self.uris.add(subject)
                if pred.startswith("<http://dbpedia.org/"):
                    self.uris.add(pred)
                if obj.startswith("<http://dbpedia.org/"):
                    self.uris.add(obj)

    def get_dash_graph(self):
        return self.graph.get_dash_graph()

    def get_rdfs_labels(self):
        sparql_uris = ', '.join(str(e) for e in self.uris)

        query = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?uri ?label {
            ?uri rdfs:label ?label
            FILTER (?uri IN (URIS_REPLACE))
            FILTER (lang(?label) = 'en')
            } 
        """.replace('URIS_REPLACE', sparql_uris)

        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        for res in results['results']['bindings']:
            label = res['label']['value']
            self.labels.add(label)
        return self.labels

    def get_ranked_rdfs_labels(self, label):
        ranked = {}
        for rdfs_label in self.labels:
            calc_distance = distance(label, rdfs_label)
            ranked[rdfs_label] = calc_distance
        sorted_labels = sorted(ranked.items(), key=lambda x: x[1], reverse=False)
        result = []
        for l, _ in sorted_labels:
            result.append({'label': l, 'value': l})
        return result
