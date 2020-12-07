#  Copyright (c) 2020
#  Rohit Suratekar, Winata Lab, IIMCB, Warsaw
#
#  This file is part of BooleanTRN project.
#  Helper functions

import json
import networkx as nx
from collections import defaultdict


def load_networks(filename) -> list:
    data = []
    with open(filename) as f:
        for line in f:
            network = json.loads(line.strip())
            data.append(network)
    return data


def find_isomorphic_networks(networks: list,
                             show_progress: bool = False) -> list:
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
    ctr = 0
    for n in networks:
        if show_progress:
            print(f"\rScanned Combinations: {ctr}", end="")
            ctr += 1
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
    return nets





