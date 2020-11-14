#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#  Analysis related to network


import json

from BooleanTRN.models.combinations import NetworkCombinations
from BooleanTRN.visualizations.networks import *
import networkx as nx


def save_networks(filename="networks.txt"):
    nc = NetworkCombinations(5, 4)
    nc.is_connected = True
    nc.gates = [0, 1]
    nc.interactions = [0, 1]
    with open(filename, "w") as f:
        for n in nc.find(["11111", "01111"], ignore_oscillations=True):
            data = json.dumps(n)
            print(data, file=f)


def load_networks():
    data = []
    with open("networks.txt") as f:
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
    for n in networks:
        graph = nx.MultiDiGraph()
        for edge in n:
            graph.add_node(edge[1], gate=edge[3])
            graph.add_edge(edge[0], edge[1], interaction=edge[2])

        if len(isomorphs) == 0:
            isomorphs.append(graph)
        else:
            tmp = [nx.is_isomorphic(x, graph,
                                    node_match=_node_condition,
                                    edge_match=_edge_condition
                                    ) for x in isomorphs]
            if not any(tmp):
                isomorphs.append(graph)
                print(len(isomorphs))


def run():
    # save_networks()
    data = load_networks()
    # nc = NetworkCombinations(5, 4)
    # ss = nc.get_state_space(data[0])
    fake = [
        (0, 1, 1, None),
    ]
    nc = NetworkCombinations(2, 1)
    print(nc.get_state_space(fake))
