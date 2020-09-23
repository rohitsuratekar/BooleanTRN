#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
# Bottom up approach

from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
from SecretColors import Palette
from SecretColors.utils import text_color
from SecretPlots import BooleanPlot

from BooleanTRN.constants import *
from BooleanTRN.models.logic import *
from BooleanTRN.models.network import Network

GREEN = Palette().green(shade=40)


def _reduce_string(string):
    def _include(ss):
        if ss == "1":
            return "T"
        elif ss == "0":
            return "F"
        else:
            raise ValueError(f"Unknown state: {ss}")

    count = 0
    letter = None
    new_string = ""
    for s in string:
        if letter is None:
            letter = s
        if s == letter:
            count += 1
        else:
            new_string += f"{count}{_include(letter)}"
            letter = s
            count = 1
    new_string += f"{count}{_include(letter)}"
    return new_string


def extract_data(network):
    all_nodes = {}
    for b in network:
        if b[0] not in all_nodes:
            all_nodes[b[0]] = Variable(b[0], True)
        for k in b[1]:
            if k not in all_nodes:
                all_nodes[k] = Variable(k, True)

    input_nodes = defaultdict(list)
    for a, b in network:
        for c in b:
            input_nodes[c].append(all_nodes[a])
    # Create data
    data = {}
    for key, item in input_nodes.items():
        if len(item) == 1:
            data[key] = item[0]
        else:
            data[key] = OR(*item)
    return data


def generate_network(network):
    p = Palette()
    data = extract_data(network)
    n = Network(data)
    graph = nx.Graph()
    initial_states = []
    for s in n.find_states():
        print(s)
        nt = [s[0]]
        initial_states.append(s[0])
        for m in [_reduce_string(x) for x in s[1]]:
            nt.append(m)
        for i in range(0, len(nt) - 1):
            graph.add_node(nt[i])
            graph.add_node(nt[i + 1])
            graph.add_edge(nt[i], nt[i + 1])

    colors = []
    labels = {}
    for i, n in enumerate(graph.nodes):
        if n in initial_states:
            labels[n] = ""
            colors.append(p.gray(shade=30))
        else:
            labels[n] = n
            colors.append(p.green())

    _, ax = plt.subplots()
    pos = nx.spring_layout(graph, seed=1989)
    nx.draw(graph, pos=pos, node_color=colors, ax=ax)

    pos_higher = {}
    for k, v in pos.items():
        pos_higher[k] = (v[0], v[1])

    nx.draw_networkx_labels(graph,
                            pos=pos_higher,
                            font_color=text_color(GREEN),
                            labels=labels,
                            bbox=dict(pad=5,
                                      fc=GREEN),
                            ax=ax)
    plt.tight_layout()
    plt.savefig("plot.png", dpi=300, transparent=True)
    plt.show()


def make_state_table(network):
    p = Palette()
    data = extract_data(network)
    n = Network(data)
    labels = list(data.keys())
    ss = []
    for s in n.find_states():
        ss.extend(s[1])
    ss = sorted(list(set(ss)))
    ss_labels = [_reduce_string(x) for x in ss]
    ss = [[int(y) for y in list(x)] for x in ss]
    cp = BooleanPlot(ss, threshold=1)
    cp.orientation = "y"
    cp.y_gap = 0.3
    cp.add_x_top_ticks()
    cp.add_x_ticklabels(labels, rotation=45, ha="left")
    cp.y_ticklabels = ss_labels
    cp.add_legends(loc='center left', bbox_to_anchor=(1, 0.5))
    cp.y_label = "Steady States"
    cp.ax.set_axisbelow(True)
    cp.show_grid = True
    cp.on_color = p.green(shade=30)
    cp.off_color = p.gray(shade=15)
    cp.save("plot.png", tight=True, dpi=300, transparent=True)
    cp.show()


def make_network(network):
    p = Palette()
    graph = nx.Graph()
    for d in network:
        graph.add_node(d[0])
        graph.add_nodes_from(d[1])
        for k in d[1]:
            graph.add_edge(d[0], k)

    # pos = nx.spring_layout(graph, seed=1, k=0.3)
    pos = nx.planar_layout(graph)
    labels = {}

    for x in graph.nodes:
        if x in BASE_NODES:
            labels[x] = x
        else:
            labels[x] = x

    _, ax = plt.subplots()
    nx.draw_networkx_nodes(graph, pos=pos,
                           has_label=False, ax=ax)
    nx.draw_networkx_edges(graph, pos=pos, ax=ax)
    for key in pos:
        x, y = pos[key]
        fc_color = p.green(shade=40)
        if key not in BASE_NODES:
            fc_color = p.gray(shade=30)
        ax.text(x, y, key,
                bbox=dict(fc=fc_color, pad=5),
                color=text_color(fc_color),
                ha="center", va="center",
                fontsize=12)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig("plot.png", dpi=300, transparent=True)
    plt.show()


def test(network):
    variables = {}
    future = defaultdict(list)
    for a, b in network:
        variables[a] = Variable(a, True)
        for c in b:
            variables[c] = Variable(c, True)
            future[c].append(a)

    data = {}
    for key, value in future.items():
        all_inputs = [variables[x] for x in value]
        data[key] = OR(*all_inputs)

    final_net = Network(data)
    final_net.print_states()


def run():
    # network = [("nkx2.5", ["gata4"])]
    network = [("a", ["b"])]
    make_network(network)
