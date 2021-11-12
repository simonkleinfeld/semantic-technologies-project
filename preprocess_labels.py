import json
import re
from time import sleep

from SPARQLWrapper import SPARQLWrapper, JSON

if __name__ == '__main__':
    question_ids = [13, 14, 15, 16, 17, 18, 21, 22, 23, 23]
    regex = "(<.*>)\s(<.*>)\s(<.*>)"
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    for qid in question_ids:
        labels = set()
        qraph_file = "resources/question_" + str(qid) + ".nxhd"
        uris = set()
        file = open(qraph_file, 'r', encoding='utf8')
        lines = file.readlines()
        for line in lines:
            res = re.match(regex, line)
            if res is not None:
                gr = res.groups()
                subject = gr[0]
                pred = gr[1]
                obj = gr[2]
                if subject.startswith("<http://dbpedia.org/"):
                    uris.add(subject)
                if pred.startswith("<http://dbpedia.org/"):
                    uris.add(pred)
                if obj.startswith("<http://dbpedia.org/"):
                    uris.add(obj)
        n = 20
        uris = list(uris)
        batches = [uris[i:i + n] for i in range(0, len(uris), n)]

        for batch in batches:
            sparql_uris = ', '.join(str(e) for e in batch)

            query = """
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        SELECT ?uri ?label {
                        ?uri rdfs:label ?label
                        FILTER (?uri IN (URIS_REPLACE))
                        FILTER (lang(?label) = 'en')
                        } 
                    """.replace('URIS_REPLACE', sparql_uris)

            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            for res in results['results']['bindings']:
                label = res['label']['value']
                labels.add(label)
            sleep(5)
            print("batch")
        j = {"labels": list(labels)}
        with open('resources/question_labels_' + str(qid) + '.json', 'w', encoding='utf8') as json_d:
            json.dump(j, json_d)
        sleep(5)
        print("file", qid)