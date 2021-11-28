from new.graph_utils import Graph
import spacy

nlp = spacy.load("en_core_web_sm")


def extract_verb_constructions_from_sent(doc):
    verb_constructions = []
    root_verb = False
    root_verb_tok = None
    contains_no_verbs = True
    for tok in doc:
        if tok.dep_ == 'ROOT' and tok.pos_ == 'VERB':
            print("Root is verb")
            root_verb = True
            root_verb_tok = tok
        if tok.pos_ == 'VERB':
            print("Contains verbs")
            contains_no_verbs = False
    if root_verb:
        triple = [None, root_verb_tok.text, None, None]
        for ch in root_verb_tok.children:
            if ch.pos_ == 'AUX':
                triple[0] = ch.text
            #if ch.dep_ == 'dobj':
            #    triple[2] = ch.text
            #if ch.dep_ == 'iobj':
            #    triple[3] = ch.text
        triple = list(filter(lambda a: a != None, triple))
        verb_constructions.append((triple, root_verb_tok.text))
    else:
        if contains_no_verbs:
            print("No Verbs Looking for AUX")
            for tok in doc:
                if tok.pos_ == 'AUX':
                    triple = [tok.text, None, None]
                    for c in tok.children:
                        #if c.dep_ == 'dobj':
                        #    triple[1] = c.text
                        #if c.dep_ == 'iobj':
                        #    triple[2] = c.text
                        c.dep
                    triple = list(filter(lambda a: a != None, triple))
                    verb_constructions.append((triple, tok.text))
        else:
            print("Looking for verbs")
            for tok in doc:
                if tok.pos_ == 'VERB':
                    triple = [None, tok.text, None, None]
                    for ch in tok.children:
                        if ch.pos_ == 'AUX':
                            triple[0] = ch.text
                        #if ch.dep_ == 'dobj':
                        #    triple[2] = ch.text
                        #if ch.dep_ == 'iobj':
                        #    triple[3] = ch.text
                    triple = list(filter(lambda a: a != None, triple))
                    verb_constructions.append((triple,tok.text))
    return verb_constructions


def construct_linear_sent_graph(doc):
    lg = []
    for token in doc:
        if not token.pos_ == 'PUNCT':
            lg.append(token.text)
    return lg


def construct_entities_list(doc):
    entities_str_lab = []
    for ent in doc.ents:
        l = ent.text.split(" ")
        entities_str_lab.append((l, l[0], ent.label_))
    return entities_str_lab


def get_noun_chunk_list(doc):
    chunk_root_list = []
    for chunk in doc.noun_chunks:
        l = chunk.text.split(" ")
        chunk_root_list.append((l, l[0]))
    return chunk_root_list


def merge_items(linear_graph, item_list, merge_root):
    new_graph = []
    found_root = False
    for i, n in enumerate(linear_graph):
        if n == merge_root:
            if len(item_list) != 1:
                if (i - 1 != 0 and linear_graph[i-1] in item_list) or (i+1 != len(linear_graph) and linear_graph[i+1] in item_list):
                    new_graph.append(" ".join(item_list))
                    found_root = True
                    continue
            else:
                new_graph.append(" ".join(item_list))
                found_root = True
                continue
        if n not in item_list or (found_root and n == merge_root):
            new_graph.append(n)
    return new_graph


def filter_items(linear_graph, item_list, edge_placeholder_text):
    new_graph = []
    for n in linear_graph:
        if n == edge_placeholder_text:
            new_graph.append(("EDGE", " ".join(item_list)))
        if n not in item_list:
            new_graph.append(n)
    if type(new_graph[-1]) == tuple:
        new_graph.append(new_graph.pop(0))
    return new_graph


def generate_dash_graph_from_linear(linear_graph):
    g = Graph()
    prev_node = None
    prev_placeholder_edge = None
    for n in linear_graph:
        if type(n) == tuple:
            prev_placeholder_edge = n[1]
        else:
            g.add_node(n,n)
            if prev_node != None:
                if prev_placeholder_edge is not None:
                    g.add_edge((n,prev_node), prev_placeholder_edge)
                    prev_placeholder_edge = None
                else:
                    g.add_edge((n,prev_node), "")
            prev_node = n
    return g.get_dash_graph()

def generate_question_graph_v2(doc):
    linear_graph = construct_linear_sent_graph(doc)
    entities_str_lab = construct_entities_list(doc)
    print(entities_str_lab)
    chunk_root_list = get_noun_chunk_list(doc)
    print(chunk_root_list)
    verb_constructions = extract_verb_constructions_from_sent(doc)
    print(verb_constructions)
    for ent in entities_str_lab:
        linear_graph = merge_items(linear_graph, ent[0], ent[1])
    for chunk in chunk_root_list:
        linear_graph = merge_items(linear_graph, chunk[0], chunk[1])
    for v in verb_constructions:
        linear_graph = filter_items(linear_graph, v[0], v[1])
    r = generate_dash_graph_from_linear(linear_graph)
    print(r)
    return r

#print(generate_question_graph_v2(nlp("Which electronics companies were founded in Beijing?")))
generate_question_graph_v2(nlp("What is the largest country in the world ? "))
generate_question_graph_v2(nlp("How many people live in Poland ?"))
generate_question_graph_v2(nlp("Who wrote Harry Potter ? "))
