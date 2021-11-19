from enum import Enum
from new.graph_utils import Graph
import spacy

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
    chunk_list = [x for x in chunk_list if x]
    print(chunk_root_list)
    print(chunk_list)
    if len(chunk_root_list) != 2:
        g.add_node(root_text, root_text)
        for chunk_root in chunk_root_list:
            g.add_node(chunk_root, chunk_root)
            g.add_edge((chunk_root, root_text))
    else:
        g.add_node(chunk_root_list[0], chunk_root_list[0])
        g.add_node(chunk_root_list[1], chunk_root_list[1])
        if len(chunk_list) == 1:
            g.add_node(chunk_list[0], chunk_list[0])
            g.add_edge((chunk_list[0], chunk_root_list[0]), "")
        if len(chunk_list) == 2:
            g.add_node(chunk_list[1], chunk_list[1])
            g.add_edge((chunk_root_list[0], chunk_root_list[1]), root_text)
        g.add_edge((chunk_root_list[0], chunk_root_list[1]), root_text)
    return g.get_dash_graph()


def generate_question_graph(processed_tokens):
    return form_question_graph_with_noun_chunks(processed_tokens)


def isNegated(tok):
    negations = ["no", "not", "n't", "never", "none"]
    for dep in list(tok.lefts) + list(tok.rights):
        if dep.lower_ in negations:
            return True, dep.lower_
    return False, dep.lower_


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
        neg, t = isNegated(root_type)
        if neg:
            root_text = t + " " + chunk.root.head.lemma_
    if root_type.pos_ != 'VERB':
        print(root_type.pos_)
        print("Non verb root, looking for potential verb dep")
        alt_root_text = None
        alt_root_type = None
        print("Looking at root children")
        for c in root_type.children:
            if c.pos_ == 'VERB':
                alt_root_type = c
                alt_root_text = c.lemma_
        if alt_root_type != None:
            print("Found Verb From Root !")
            root_text = alt_root_text.lemma_
            root_type = alt_root_type
            neg, t = isNegated(root_type)
            if neg:
                root_text = t + " " + alt_root_text.lemma_
        else:
            print("Looking across question for main verb")
            verbs = [tok for tok in processed_tokens if tok.pos_ == "VERB"]
            if len(verbs) == 0:
                print("No verbs found !")
            else:
                m = -1
                max_v = None
                for v in verbs:
                    l = list(v.children)
                    if len(l) > m:
                        m = len(l)
                        max_v = v
                neg, t = isNegated(max_v)
                root_type = max_v
                if neg:
                    root_text = t + " "+max_v.text
                else:
                    root_text = max_v.text
    if chunk_processing_algorithm == CHUNK_PROCESSING_ALGORITHM.UNI_GRAM_USING_ROOTS:
        return generate_uni_gram_graph_from_chunks(chunk_list, chunk_list_roots, root_text)



def get_qsvo_triple_from_root(question):
    SUBJECTS_DEP = ["nsubj", "nsubjpass", "csubj", "csubjpass"]
    SUBJECTS_POS = ['NOUN', 'PROPN', 'DET']
    OBJECT_DEP = ["dobj", "iobj"]
    OBJECT_POS = ['NOUN', 'PROPN']
    ROOT = "ROOT"
    processed_tokens = []
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