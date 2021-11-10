from typing import Tuple

import numpy
from numpy import dot
from numpy.linalg import norm


class Graph:

    def __init__(self):
        self.node_neighbors = {}  # Pairing: Node to Neighbors
        self.edge_attr = {}
        self.node_attr = {}

    def breadth_first_search(self, label, gensim, root=None):
        visited = {}
        queue = []
        s = list(self.node_neighbors.keys()).pop(0)
        queue.append(s)
        visited[s] = True
        while queue:
            s = queue.pop(0)
            str_lab = self.get_node_label(s)
            lab = self.get_node_vec(s)
            label_vec = []
            try:
                label_vec = gensim.wv[label]
            except Exception as e:
                pass
            if label_vec != []:
                if dot(lab, label_vec) / (norm(lab) * norm(label_vec)) > 0.95:
                    return s
            if str_lab == label:
                return s
            for e in self.get_edges_for_node(s):
                if visited[e[1]] == False:
                    queue.append(e[1])
                    visited[e[1]] = True
        return None

    def get_edge_vec(self, edge: Tuple[str, str]):
        return self.edge_attr.get(edge)['vec']

    def get_node_vec(self, node: str):
        return self.node_attr.get(node)['vec']

    def get_edge_label(self, edge: Tuple[str, str]):
        return self.edge_attr.get(edge)['label']

    def get_node_label(self, node: str):
        return self.node_attr.get(node)['label']

    def get_edges_for_node(self, node: str):
        edge_list = []
        for e in self.edges():
            if node in e:
                edge_list.append(e)
        return edge_list

    def nodes(self):
        return list(self.node_neighbors.keys())

    def neighbors(self, node):
        return list(self.node_neighbors[node])

    def edges(self):
        return [a for a in self.edge_attr.keys()]

    def has_node(self, node):
        return node in self.node_neighbors

    def convert_token_list_to_vec(self, label_tokens, gensim, dim):
        sent_vec = numpy.zeros(dim)
        for tok in label_tokens:
            try:
                sent_vec = sent_vec + gensim.wv[tok]
            except Exception as e:
                continue
        if len(label_tokens) > 0:
            return sent_vec * (1.0 / len(label_tokens))
        return sent_vec

    def add_node(self, node: str, gensim, dim, label='', label_tokens=None, vec=None):
        if vec is None:
            vec = []
        if label_tokens is None:
            label_tokens = []
        if not node in self.node_neighbors:
            self.node_neighbors[node] = set()
            if label_tokens != []:
                self.node_attr[node] = {"label": label,
                                        "vec": self.convert_token_list_to_vec(label_tokens, gensim, dim)}
                return
            if vec != []:
                self.node_attr[node] = {"label": label, "vec": vec}
                return

    # edge consists of (node_id, node_id)
    def add_edge(self, edge: Tuple[str, str], gensim, dim, label='', label_tokens=None, vec=None):
        if vec is None:
            vec = []
        if label_tokens is None:
            label_tokens = []
        u, v = edge
        if (v not in self.node_neighbors[u] and u not in self.node_neighbors[v]):
            self.node_neighbors[u].add(v)
            if (u != v):
                self.node_neighbors[v].add(u)
            if label_tokens != []:
                self.edge_attr[(u, v)] = {"label": label,
                                          "vec": self.convert_token_list_to_vec(label_tokens, gensim, dim)}
                return
            if vec != []:
                self.edge_attr[(u, v)] = {"label": label, "vec": vec}
                return

    def del_node(self, node: str):
        for each in list(self.neighbors(node)):
            if (each != node):
                self.del_edge((each, node))
        del (self.node_neighbors[node])
        del (self.node_attr[node])

    def del_edge(self, edge: Tuple[str, str]):
        u, v = edge
        self.node_neighbors[u].remove(v)
        self.del_edge_labeling((u, v))
        if (u != v):
            self.node_neighbors[v].remove(u)
            self.del_edge_labeling((v, u))

    def has_edge(self, edge: Tuple[str, str]):
        u, v = edge
        return (u, v) in self.edge_attr and (v, u) in self.edge_attr

    def node_order(self, node: str):
        return len(self.neighbors(node))

    def del_edge_labeling(self, edge):
        self.edge_attr[edge].remove()

    def get_dash_graph(self):
        nodes = []
        for v in self.node_neighbors:
            nodes.append({'data': {'id': v, 'label': self.node_attr[v]['label']}})
        for e in self.edge_attr:
            nodes.append({'data': {'source': e[0], 'target': e[1], 'label': self.edge_attr[e]['label']}})
        return nodes
