from enum import Enum
from new.graph_utils import Graph
import spacy

nlp = spacy.load("en_core_web_sm")

#https://universaldependencies.org/u/pos/
#https://universaldependencies.org/docs/en/dep/


class CHUNK_PROCESSING_ALGORITHM(Enum):
    UNI_GRAM_USING_ROOTS = 1
    DEPENDENCY_RE_PARSE_CHUNKS = 2


def generate_uni_gram_graph_from_chunks(chunk_list, chunk_root_list, root_text):
    g = Graph()
    for i, chunk_root in enumerate(chunk_root_list):
        t = chunk_list[i].replace(chunk_root, "")
        chunk_list[i] = t
    print(chunk_root_list)
    if len(chunk_root_list) != 2:
        g.add_node(root_text, root_text)
        for chunk_root in chunk_root_list:
            g.add_node(chunk_root, root_text)
            g.add_edge((chunk_root, root_text))
    else:
        g.add_node(chunk_list[0], chunk_list[0])
        g.add_node(chunk_list[1], chunk_list[1])
        g.add_node(chunk_root_list[0], chunk_root_list[0])
        g.add_node(chunk_root_list[1], chunk_root_list[1])
        g.add_edge((chunk_list[0], chunk_root_list[0]), "")
        g.add_edge((chunk_list[1], chunk_root_list[1]), "")
        g.add_edge((chunk_root_list[0], chunk_root_list[1]), root_text)
    return g.get_dash_graph()


def generate_question_graph(question):
    processed_tokens = nlp(question)
    return form_question_graph_with_noun_chunks(processed_tokens)


def form_question_graph_with_noun_chunks(processed_tokens, chunk_processing_algorithm=CHUNK_PROCESSING_ALGORITHM.UNI_GRAM_USING_ROOTS):
    ROOT = "ROOT"
    chunk_list_roots = []
    chunk_list = []
    root_text = None
    root_type = None
    for chunk in processed_tokens.noun_chunks:
        chunk_list.append(chunk.text)
        chunk_list_roots.append(chunk.root.text)
        root_text = chunk.root.head.lemma_
        root_type = chunk.root.head
    if root_type.pos_ != 'VERB':
        print(root_type.pos_)
        print("Non verb root, results may be wrong")
    if chunk_processing_algorithm == CHUNK_PROCESSING_ALGORITHM.UNI_GRAM_USING_ROOTS:
        return generate_uni_gram_graph_from_chunks(chunk_list, chunk_list_roots, root_text)



def get_qsvo_triple_from_root(question):
    SUBJECTS_DEP = ["nsubj", "nsubjpass", "csubj", "csubjpass"]
    SUBJECTS_POS = ['NOUN', 'PROPN', 'DET']
    OBJECT_DEP = ["dobj", "iobj"]
    OBJECT_POS = ['NOUN', 'PROPN']
    ROOT = "ROOT"
    processed_tokens = nlp(question)
    qsvo = {'q' : '', 's': '', 'v': '', 'o': ''}
    root_tok = [tok for tok in processed_tokens if tok.pos_ == ROOT][0]
    if root_tok.pos_ == 'VERB':
        qsvo['v'] = root_tok.lemma
    else:
        print("Non verb root")
        return qsvo
    root_children = [child for child in root_tok.children]
    possible_subjects = []
    possible_objects = []
    for n in root_children:
        if n.dep_ in SUBJECTS_DEP:
            possible_subjects.append(n)
        if n.dep_ in OBJECT_DEP:
            possible_objects.append(n)

print(generate_question_graph("Which countries have more than ten volcanoes?"))
print(generate_question_graph("What are the five boroughs of New York?"))
print(generate_question_graph("How short is the shortest active NBA player?"))
print(generate_question_graph("What is Elon Musk famous for?"))
print(generate_question_graph("In what city is the Heineken brewery?"))
print(generate_question_graph("What is the atmosphere of the Moon composed of?"))

print(generate_question_graph("Which electronics companies were founded in Beijing?"))

