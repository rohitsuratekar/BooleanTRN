#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
#
#  This file is part of BooleanTRN project.
#

from typing import List

import networkx as nx

from BooleanTRN.models.functions import generate_state_space
from BooleanTRN.visualizations.network import *

BASE_NETWORK = [
    ('nkx2.5', ['tbx5a', 'mef2ca', 'gata4', 'hand2']),
    ('gata4', ['hand2', 'mef2ca', 'tbx5a']),
    ('tbx5a', ['nkx2.5'])
]


def get_base_network():
    net = []
    for d in BASE_NETWORK:
        for k in d[1]:
            net.append((d[0], k, 1))
    return net


def get_data() -> List[tuple]:
    data = [
        ("nkx2.5", "gata4", 1),
        ("nkx2.5", "tbx5a", 1),
        ("gata4", "nkx2.5", 1),
    ]
    return data


def map_colors(space):
    p = Palette()
    g = nx.DiGraph()
    for key, value in space.items():
        g.add_edge(key, value)
    colors = {}
    for c in nx.attracting_components(g):
        if len(c) == 1:
            colors[list(c)[0]] = p.green(shade=30)
        else:
            for cs in c:
                colors[cs] = p.violet(shade=30)

    return colors


def analyse_transitions():
    d = get_base_network()
    d.append(("External Signal", "nkx2.5", 1))
    d.append(("tbx5a", "gata4", 1))
    d.remove(("tbx5a", "nkx2.5", 1))

    node_order = ["nkx2.5", "gata4", "tbx5a",
                  "hand2", "mef2ca", "External Signal"]

    nodes, space, _ = generate_state_space(d, gate="OR", node_order=node_order)
    colors = map_colors(space)
    plot_transition_graph(space, color_mapping=colors, layout="neato",
                          graph_opt={"start": "random15"})
    print(f"Node Order: [ {', '.join(nodes)} ]")


def example_graph():
    space = {"00111": "00100", "00100": "10111", "10111": "10011",
             "10011": "11111"}
    colors = {"11111": Palette().green(shade=30)}
    g = plot_transition_graph(space, color_mapping=colors, layout="dot")
    gc = GraphAdjustment(g)
    gc.add_edge(("11000", "10011", 1))
    gc.graph.get_edge("11000", "10011").attr["minlen"] = 3
    gc.graph.add_subgraph(["11000", "10011"], rank="same")
    gc.draw()


def analyse_network():
    signal = "External Signal"
    d = get_base_network()
    d.append((signal, "nkx2.5", 1))
    g = plot_network(d)
    ga = GraphAdjustment(g)
    ga.remove_edge("tbx5a", "nkx2.5")
    ga.node_to_text(signal)
    ga.add_edge(("tbx5a", "gata4", 1))
    ga.graph.add_subgraph(["tbx5a", "hand2", "mef2ca"], rank="sink")
    ga.mutant("hand2")
    ga.draw()


def run():
    analyse_network()
    # analyse_transitions()
    # example_graph()
