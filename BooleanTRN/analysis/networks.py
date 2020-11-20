#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#  Analysis related to network


import json
from collections import defaultdict

from BooleanTRN.models.combinations import NetworkCombinations
from BooleanTRN.visualizations.networks import *
from BooleanTRN.visualizations.graph_properties import *
import networkx.algorithms as algo


def save_networks(filename="networks.txt", nodes=1, edges=1):
    nc = NetworkCombinations(nodes, edges)
    nc.is_connected = True
    nc.gates = [0, 1]
    nc.interactions = [0, 1]
    with open(filename, "w") as f:
        for n in nc.find(["11111", "01111"], show_progress=True):
            data = json.dumps(n)
            print(data, file=f)


def load_networks(filename):
    data = []
    with open(filename) as f:
        for line in f:
            network = json.loads(line.strip())
            data.append(network)
    return data


def find_isomorphic_networks(networks):
    def _node_condition(n1, n2):
        try:
            return n1["gate"] == n2["gate"]
        except KeyError:
            return True

    def _edge_condition(e1, e2):
        if len(e1.keys()) > 1 or len(e2.keys()) > 1:
            print(e1, e2)
        return e1[0]["interaction"] == e2[0]["interaction"]

    isomorphs = []
    nets = []
    for n in networks:
        graph = nx.MultiDiGraph()
        for edge in n:
            graph.add_node(edge[1], gate=edge[3])
            graph.add_edge(edge[0], edge[1], interaction=edge[2])

        if len(isomorphs) == 0:
            isomorphs.append(graph)
            nets.append(n)
        else:
            tmp = [nx.is_isomorphic(x, graph,
                                    node_match=_node_condition,
                                    edge_match=_edge_condition
                                    ) for x in isomorphs]
            if not any(tmp):
                isomorphs.append(graph)
                nets.append(n)

    with open("isomorphs.txt", "w") as f:
        for n in nets:
            print(json.dumps(n), file=f)


def steady_state_isomorphs(networks, nc: NetworkCombinations):
    graphs = []
    nets = defaultdict(list)
    for n in networks:
        g = nx.MultiDiGraph()
        for ss in nc.get_state_space(n).items():
            g.add_edge(ss[0], ss[1])
        if len(graphs) == 0:
            graphs.append(g)
            nets[g].append(n)
        else:
            tmp = [nx.is_isomorphic(x, g) for x in graphs]
            if not any(tmp):
                graphs.append(g)
                nets[g].append(n)
            else:
                nets[graphs[tmp.index(True)]].append(n)
    del graphs
    return list(nets.values())


def find_node_properties(networks):
    degree_in = defaultdict(list)
    degree_out = defaultdict(list)
    for n in networks:
        graph = nx.MultiDiGraph()
        for k in n:
            graph.add_edge(k[0], k[1])

        for i in graph.in_degree:
            degree_in[i[0]].append(i[1])

        for i in graph.out_degree:
            degree_out[i[0]].append(i[1])

    plot_node_degrees(degree_out, "Out Degree")


def run():
    # save_networks(nodes=5, edges=5)
    nc = NetworkCombinations(5, 6)
    data = load_networks("sample_data/isomorphs_n5_e6.txt")
    nets = steady_state_isomorphs(data, nc)
    find_node_properties(nets[4])
    # plot_transition_graph(nc.get_state_space(nets[4][0]))
    # plot_multiple_networks(nets[4][:25], figsize=(8, 8), mark=0)
