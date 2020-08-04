#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#

import itertools
from collections import defaultdict
from typing import List

import networkx as nx
from SecretColors import Palette


class Edge:
    def __init__(self, data):
        self.origin = data[0]
        self.destination = data[1]
        self.type = bool(data[2])


def _solve_network(data: List[Edge], nodes: List[str], states: tuple) -> list:
    tmp = defaultdict(list)
    for d in data:
        idx = nodes.index(d.origin)
        if d.type:
            tmp[d.destination].append(states[idx])
        else:
            tmp[d.destination].append(int(not bool(states[idx])))

    final_states = []
    for n in nodes:
        if n in tmp.keys():
            # IMPORTANT: Assume everything is in OR configuration
            final_states.append(max(tmp[n]))
        else:
            # Return the original state
            final_states.append(states[nodes.index(n)])

    return final_states


def _convert(state):
    return "".join([str(x) for x in state])


def _parse_data(data):
    network = []
    for d in data:
        for k in d[1]:
            network.append((d[0], k, 1))
    return network


def _make_transition_graph(data: list, remove_redundant: bool) -> dict:
    red_nodes = []
    if remove_redundant:
        red_nodes = _get_leaves(data)
        print(f"Following {len(red_nodes)} redundant node(s) removes from "
              f"transition graph")
        print(red_nodes)

    # Extract all nodes
    nodes = [y for x in data for y in x[:2] if y not in red_nodes]
    data = [Edge(x) for x in data]
    nodes = list(set(nodes))  # Get unique nodes
    tmp = itertools.repeat([0, 1], len(nodes))
    state_space = {}
    for x in itertools.product(*tmp):
        x_str = _convert(x)
        if x_str not in state_space.keys():
            state_space[x_str] = _convert(
                _solve_network(data, nodes, x))
    return state_space


def _get_leaves(data: list):
    source_nodes = set([x[0] for x in data])
    sink_nodes = set([x[1] for x in data])
    leaves = sink_nodes - source_nodes
    return list(leaves)


def plot_transition_graph(data: list, remove_redundant: bool = False):
    data = _make_transition_graph(data, remove_redundant)
    p = Palette()
    g = nx.MultiDiGraph()
    for key in data:
        g.add_edge(key, data[key])

    g.graph['graph'] = {
        'dpi': 300,
        'sep': 5,
        'start': 1989
    }
    g.graph['node'] = {
        'fontsize': 12,
        'shape': 'ellipse',
        'height': 0,
        'width': 0,
        'margin': 0.03
    }
    g.graph['edge'] = {
        'arrowsize': 0.8,
        'headclip': True
    }
    a = nx.drawing.nx_agraph.to_agraph(g)
    a.layout('neato')
    # a.layout('dot')

    aa = nx.drawing.nx_agraph.from_agraph(a)
    for at in nx.attracting_components(aa):
        if len(at) == 1:
            n = a.get_node(list(at)[0])
            n.attr['style'] = 'filled'
            n.attr['fillcolor'] = p.green(shade=30)
        else:
            for sub in at:
                n = a.get_node(sub)
                n.attr['style'] = 'filled'
                n.attr['fillcolor'] = p.violet(shade=30)

    a.draw('plot.png')


def plot_network(data: list):
    p = Palette()
    g = nx.MultiDiGraph()
    for d in data:
        arrowhead = "normal"
        if not d[2]:
            arrowhead = "dot"
        g.add_edge(d[0], d[1], arrowhead=arrowhead)

    g.graph['graph'] = {
        'dpi': 300,
        'start': 1989,
        'sep': 2,
        'rankdir': 'LR'
    }
    g.graph['node'] = {
        'fontsize': 12,
        'shape': 'ellipse',
        'height': 0,
        'width': 0,
        'style': 'filled',
        'fillcolor': p.peach(shade=20),
        'margin': 0.03
    }
    g.graph['edge'] = {
        'arrowsize': 0.8,
        # 'len': 2
    }

    a = nx.drawing.nx_agraph.to_agraph(g)
    # a.layout('neato')
    a.layout('dot')
    a.draw("plot.png")


def run():
    from BooleanTRN.constants import EXTENDED_NETWORK
    data = [
        ("a", "b", 1),
        ("c", "b", 0),
        ("b", "d", 0),

    ]
    data = _parse_data(EXTENDED_NETWORK)
    # plot_transition_graph(data, True)
    plot_network(data)
