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
from SecretColors.utils import text_color


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
            # TODO: Proper Logic
            # IMPORTANT: Assume everything is in OR configuration
            final_states.append(max(tmp[n]))  # Assume all OR Gates
            # final_states.append(min(tmp[n]))  # Assume all AND Gates
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
        red_nodes = _get_redundant(data)
        print(f"Following {len(red_nodes)} redundant node(s) removes from "
              f"transition graph")
        print(red_nodes)

    # Extract all nodes
    nodes = [y for x in data for y in x[:2] if y not in red_nodes]
    data = [Edge(x) for x in data]
    nodes = list(set(nodes))  # Get unique nodes
    nodes = sorted(nodes)  # Just for reproducibility
    print("Following is node order")
    print(nodes)
    tmp = itertools.repeat([0, 1], len(nodes))
    state_space = {}
    for x in itertools.product(*tmp):
        x_str = _convert(x)
        if x_str not in state_space.keys():
            state_space[x_str] = _convert(
                _solve_network(data, nodes, x))
    return state_space


def _get_redundant(data: list):
    source_nodes = set([x[0] for x in data])
    sink_nodes = set([x[1] for x in data])
    leaves = sink_nodes - source_nodes
    return list(leaves)


def plot_transition_graph(data: list,
                          remove_redundant: bool = False,
                          keep_only_stable: bool = False,
                          layout: str = "dot",
                          is_state_space: bool = False):
    data = _make_transition_graph(data, remove_redundant)
    p = Palette()
    g = nx.DiGraph()
    for key in data:
        g.add_edge(key, data[key])

    node_shape = "ellipse"
    arrow = "normal"
    arrow_style = "filled"
    if keep_only_stable:
        node_shape = "point"
    if is_state_space or keep_only_stable:
        arrow = "none"
        arrow_style = "invisible"

    g.graph['graph'] = {
        'dpi': 300,
        'smoothing': 'spring',
        'start': 'random100',
        "bgcolor": "transparent"
    }
    g.graph['node'] = {
        'fontsize': 11,
        'fontname': 'IBM Plex Sans',
        'shape': node_shape,
        'height': 0,
        'width': 0,
        'margin': 0.04,
        'style': 'filled',
        'fillcolor': p.gray(shade=10)
    }
    g.graph['edge'] = {
        'arrowsize': 0.8,
        'arrowhead': arrow,
        'style': arrow_style
    }

    a = nx.drawing.nx_agraph.to_agraph(g)
    aa = nx.drawing.nx_agraph.from_agraph(a)

    def _style_node(n1, c1):
        n1.attr['shape'] = "ellipse"
        n1.attr['fillcolor'] = c1
        n1.attr['fontcolor'] = text_color(c1)

    for de in nx.nodes(g):
        if nx.degree(g, de) > 1 or is_state_space:
            ne = a.get_node(de)
            de_color = p.gray(shade=25)
            ne.attr['shape'] = "ellipse"
            ne.attr['fillcolor'] = de_color
            ne.attr['fontcolor'] = text_color(de_color)

    if not is_state_space:
        for at in nx.attracting_components(aa):
            if len(at) == 1:
                n = a.get_node(list(at)[0])
                _style_node(n, p.green(shade=30))
            else:
                for sub in at:
                    n = a.get_node(sub)
                    _style_node(n, p.violet(shade=30))

    a.layout(layout)
    a.draw('plot.png')


def plot_network(data: list, layout="dot", mutant: str = None, off_nodes=None):
    p = Palette()
    g = nx.DiGraph()
    for d in data:
        arrowhead = "normal"
        if not d[2]:
            arrowhead = "dot"
        g.add_edge(d[0], d[1], arrowhead=arrowhead)

    g.graph['graph'] = {
        'dpi': 300,
        'start': 'random1989',
        'smoothing': 'spring',
        # 'rankdir': 'LR',
        "bgcolor": "transparent",
    }
    f_color = p.ultramarine(shade=20)
    g.graph['node'] = {
        'fontsize': 12,
        'fontname': 'IBM Plex Sans',
        'shape': 'ellipse',
        'height': 0,
        'width': 0,
        'style': 'filled',
        'fillcolor': f_color,
        'margin': 0.04,
        'fontcolor': text_color(f_color)
    }
    g.graph['edge'] = {
        'arrowsize': 0.8,
        'len': 1.2
    }

    a = nx.drawing.nx_agraph.to_agraph(g)
    a.layout(layout)

    if off_nodes is not None:
        for gn in a.nodes():
            if gn not in off_nodes:
                continue
            ne = a.get_node(gn)
            de_color = p.magenta(shade=20)
            ne.attr['shape'] = "ellipse"
            ne.attr['fillcolor'] = de_color
            ne.attr['fontcolor'] = text_color(de_color)

    if mutant:
        ne = a.get_node(mutant)
        de_color = p.red(shade=25)
        ne.attr['shape'] = "ellipse"
        ne.attr['fillcolor'] = de_color
        ne.attr['fontcolor'] = text_color(de_color)
        for d in data:
            e = None
            if d[0] == mutant:
                e = a.get_edge(mutant, d[1])
            elif d[1] == mutant:
                e = a.get_edge(d[0], mutant)
            if e:
                e.attr['color'] = p.gray()
                e.attr['style'] = "dashed"
                e.attr['arrowhead'] = "none"

    for inv in ["ES"]:
        a.get_node(inv).attr["style"] = "invis"
        for e in a.edges():
            if inv in e:
                e.attr["color"] = p.gray(shade=20)

    # a.get_node("nkx2.5").attr["fillcolor"] = p.red(shade=20)
    a.get_edge("a", "mef2ca").attr["style"] = "dashed"
    a.get_edge("a", "mef2ca").attr["color"] = p.black()

    a.draw("plot.png")


def run():
    from BooleanTRN.constants import BASE_NETWORK
    data = _parse_data(BASE_NETWORK)
    data.append(("ES", "nkx2.5", 1))
    layout = "dot"
    layout = "neato"

    plot_transition_graph(data, layout=layout, remove_redundant=True)
    # plot_network(data, layout=layout)
