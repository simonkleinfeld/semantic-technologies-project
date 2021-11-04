import re

from itertools import chain, combinations
import dash_cytoscape as cyto
import numpy
from dash import dcc, html
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
from tabs.graph import Graph
from numpy import dot
from numpy.linalg import norm
from thefuzz import fuzz


DIM_GENSIM = 50

question_graph_tab = dcc.Tab(label='Question Graph', children=[
    html.Div(id='output-question', style={'margin': 8}, children=[
        html.Div(id='output-question-div-1', style={'margin': 8}, children=[
            html.Button('Question Tree 1', id='question-tree-button-1', style={'margin': 8}, n_clicks=0),
            html.Button('Question Tree 2', id='question-tree-button-2', style={'margin': 8}, n_clicks=0),
        ]),
        html.Div(id='output-question-div-2', style={'margin': 8, 'height': 'calc(100vh - 200px)',
                                                    'width': '100vh', }, children=[
            cyto.Cytoscape(
                id='question-graph',
                elements=[],
                layout={
                    'name': 'concentric'
                },
                style={
                    "width": "100%",
                    "height": "100%"
                },
                stylesheet=[
                    {'selector': 'edge', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
                    {'selector': 'node', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
                ]
            )
        ])
    ])
])

def branch_nodes_with_limit(graph: Graph, active_nodes, no_tokens):
    branched_set = set(active_nodes)
    for i in range(0, no_tokens):
        current_l = list(branched_set)
        for v in current_l:
            neighb = graph.neighbors(v)
            for n in neighb:
                branched_set.add(n)
    return branched_set


def get_bounded_neighbourhood_graph(graph, no_tokens, keyword, gensim):
    start_node = graph.breadth_first_search(keyword, gensim)
    branched_set = set()
    branched_set.add(start_node)
    for i in range(0, no_tokens):
        current_l = list(branched_set)
        for v in current_l:
            neighb = graph.neighbors(v)
            for n in neighb:
                branched_set.add(n)
    edge_set = set()
    neighbourhood_graph = Graph()
    for v in branched_set:
        for e in graph.get_edges_for_node(v):
            edge_set.add(e)
        neighbourhood_graph.add_node(v, graph.get_node_label(v), gensim, DIM_GENSIM, vec=graph.get_node_vec(v))
    for e in edge_set:
        neighbourhood_graph.add_edge(e, graph.get_edge_label(e), gensim, DIM_GENSIM, vec=graph.get_edge_vec(e))
    return neighbourhood_graph, start_node


def get_n_gram_of_token_list(token_list, n=3):
    return [token_list[i:i+n] for i in range(len(token_list)-n+1)]

def get_vector_for_token(tok, gensim):
    sent_vec = numpy.zeros(DIM_GENSIM)
    try:
        sent_vec = gensim.wv[tok]
        return sent_vec
    except Exception as e:
        return sent_vec


def get_lev_similarity(a_str, b_str):
    if (type(a_str) != str):
        a_str = str(a_str)
    if (type(b_str) != str):
        b_str = str(b_str)
    lev_dist = fuzz.ratio(a_str, b_str)
    if lev_dist != 0.0:
        return lev_dist/100
    return 0.0

def get_similarity(a_vec, b_vec, a_str, b_str):
    cos_sim = dot(a_vec, b_vec) / (norm(a_vec) * norm(b_vec))
    if cos_sim != 0.0 and not numpy.isnan(cos_sim):
        return cos_sim
    if (type(a_str) != str):
        a_str = str(a_str)
    if (type(b_str) != str):
        b_str = str(b_str)
    lev_dist = fuzz.ratio(a_str, b_str)
    if lev_dist != 0.0:
        return lev_dist/100
    return 0.0


def local_search_algorithm(graph_structure: Graph, token_list, keyword, gensim):
    neighbourhood_graph, keyword_node = get_bounded_neighbourhood_graph(graph_structure, len(token_list), keyword, gensim)
    tri_gram_list = get_n_gram_of_token_list(token_list)
    current_node = keyword_node
    current_node_vec = neighbourhood_graph.get_node_vec(current_node)
    active_tokens = token_list.copy()
    result_graph = Graph()
    result_graph.add_node(current_node, gensim, DIM_GENSIM, neighbourhood_graph.get_node_label(current_node), vec=neighbourhood_graph.get_node_vec(current_node))
    while(len(active_tokens) != 0):
        candidate_nodes = []
        candidate_edges = []
        max_sim = 0.0
        max_tok = ""
        for tok in active_tokens:
            for e in neighbourhood_graph.get_edges_for_node(current_node):
                edge_l = neighbourhood_graph.get_edge_vec(e)
                cos_sim = get_similarity(get_vector_for_token(tok, gensim), edge_l, tok, neighbourhood_graph.get_edge_label(e))
                if cos_sim == max_sim:
                    candidate_nodes.append(e[1])
                    candidate_nodes.append(e[0])
                    candidate_edges.append(e)
                if cos_sim > max_sim:
                    max_sim = cos_sim
                    candidate_nodes.clear()
                    candidate_edges.clear()
                    candidate_nodes.append(e[1])
                    candidate_nodes.append(e[0])
                    candidate_edges.append(e)
                    max_tok = tok
        if max_tok != "":
            active_tokens.remove(max_tok)
        else:
            active_tokens.pop(0)
        for v in candidate_nodes:
            result_graph.add_node(v, neighbourhood_graph.get_node_label(v), gensim, DIM_GENSIM, vec=neighbourhood_graph.get_node_vec(v))
        # determine forward_path
        max_forward_path = -1.0
        forward_node = ""
        for e in candidate_edges:
            result_graph.add_edge(e, neighbourhood_graph.get_edge_label(e), gensim, DIM_GENSIM, vec=neighbourhood_graph.get_edge_vec(e))
            triple_labels = [neighbourhood_graph.get_node_label(current_node), neighbourhood_graph.get_edge_label(e), neighbourhood_graph.get_node_label(e[1])]
            triple_vecs = [current_node_vec, neighbourhood_graph.get_edge_vec(e), neighbourhood_graph.get_node_vec(e[1])]
            forward_node_candidate = e[1]
            for ngram in tri_gram_list:
                z_lab = list(zip(ngram, triple_labels))
                s = 0.0
                for i in z_lab:
                    s += get_lev_similarity(i[0],i[1])
                if s > max_forward_path:
                    max_forward_path = s
                    forward_node = forward_node_candidate
        current_node = forward_node
        if current_node == "":
            break
        current_node_vec = neighbourhood_graph.get_node_vec(current_node)
    return result_graph

def convert_uri_to_string_label(uri):
    url_path = PurePosixPath(unquote(urlparse(uri).path))
    string = url_path.name
    if type(string) != str:
        string = str(string)
    for c in ["_", "-", "#", "(", ")"]:
        if c in string:
            string = string.replace(c, " ")
    return string

def create_question_graph(file, doc, gensim):
    graph_structure = get_graph_structure(file, gensim)
    token_list = []
    #TODO: get keyword for now take first entity
    keyword = ""
    for ent in doc.ents:
        keyword = ent.text
        break
    for tok in doc:
        if tok.pos_ == 'PUNCT' or tok.pos_ == 'SYM' or tok.pos_ == 'X':
            continue
        token_list.append(tok.text)
    result_graph = local_search_algorithm(graph_structure, token_list, keyword, gensim)
    return result_graph.get_dash_graph()

def get_graph_structure(file, gensim):
    file1 = open(file, 'r')
    lines = file1.readlines()
    existing_nodes = set()
    lines_ = []
    nodes = []
    regex = "<(.*)>\s<(.*)>\s<(.*)>"
    graph = Graph()
    for line in lines:
        res = re.match(regex, line)
        if res is not None:
            gr = res.groups()
            lines_.append(gr)
            subject = gr[0]
            pred = gr[1]
            obj = gr[2]
            if subject not in existing_nodes:
                s = convert_uri_to_string_label(subject)
                sl = s.split(" ")
                graph.add_node(subject, gensim, DIM_GENSIM, s, sl)
            if obj not in existing_nodes:
                s = convert_uri_to_string_label(obj)
                sl = s.split(" ")
                graph.add_node(obj, gensim, DIM_GENSIM, s, sl)
                existing_nodes.add(obj)
            p = convert_uri_to_string_label(pred)
            pl = p.split(" ")
            graph.add_edge((subject, obj), gensim, DIM_GENSIM, p, pl)
    return graph

def create_question_content(file):
    file1 = open(file, 'r')
    lines = file1.readlines()
    existing_nodes = set()
    lines_ = []
    nodes = []
    regex = "<(.*)>\s<(.*)>\s<(.*)>"
    graph = Graph()
    for line in lines:
        res = re.match(regex, line)
        if res is not None:
            gr = res.groups()
            lines_.append(gr)
            subject = gr[0]
            pred = gr[1]
            obj = gr[2]
            if subject not in existing_nodes:
                s = convert_uri_to_string_label(subject)
                sl = s.split(" ")
                graph.add_node(subject, None, DIM_GENSIM, s, sl, vec=[0]*50)
            if obj not in existing_nodes:
                s = convert_uri_to_string_label(obj)
                sl = s.split(" ")
                graph.add_node(obj, None, DIM_GENSIM, s, sl, vec=[0]*50)
                existing_nodes.add(obj)
            p = convert_uri_to_string_label(pred)
            pl = p.split(" ")
            graph.add_edge((subject, obj), None, DIM_GENSIM, p, pl, vec=[0]*50)
    return graph.get_dash_graph()