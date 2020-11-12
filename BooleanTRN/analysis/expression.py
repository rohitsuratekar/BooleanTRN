#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#

import json
from collections import Counter

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx

from BooleanTRN.models.sweeps import NetworkAnalyser
from BooleanTRN.models.sweeps import RawNetwork
from BooleanTRN.visualizations.network import *

matplotlib.rc("font", family="IBM Plex Sans")


def search_networks():
    na = NetworkAnalyser(5, 4, allow_negative=True)
    na.gates = [0, 1]
    na.is_connected = True
    target_states = ["11111", "01111"]
    data = []
    for n in na.find_networks(target_states, strict=True):
        data.append(n)

    save_data = {}
    for i, d in enumerate(data):
        save_data[i] = d

    with open("networks.json", "w") as f:
        json.dump(save_data, f)


def extract_networks():
    p = Palette()
    with open("data/five_node_networks.json") as f:
        data = json.load(f)

    extracted = []
    cn = Counter()
    for d in data.values():
        d = {int(x): d[x] for x in d.keys()}
        if len(extracted) == 0:
            extracted.append(RawNetwork(d))
        else:
            tmp = RawNetwork(d)
            chk = [nx.is_isomorphic(x.undirected(),
                                    tmp.undirected()) for x in extracted]
            if not any(chk):
                extracted.append(tmp)
            else:
                cn.update({chk.index(True)})

    for i in range(len(extracted)):
        filename = f"graph{i + 1}.png"
        print(i, cn[i])
        print(extracted[i].data)
        ax = plot_network(extracted[i].edges,
                          filename=filename)
        gc = GraphAdjustment(ax)
        gc.filename = filename
        gc.change_label(0, "Nkx2.5")
        gc.highlight(0, p.green_light(shade=40))
        gc.draw()


def get_similar(network):
    graph = RawNetwork(network)
    with open("data/five_node_networks.json") as f:
        data = json.load(f)

    similar = []
    for d in data.values():
        d = {int(x): d[x] for x in d.keys()}
        tmp = RawNetwork(d)
        if nx.is_isomorphic(graph.undirected(), tmp.undirected()):
            similar.append(d)

    return similar


def make_network_flow(network):
    p = Palette()

    similar = get_similar(network)

    cn = Counter()
    for s in similar:
        for des in s:
            gate = s[des][0]
            for source in s[des][1]:
                cn.update({(source[0], des, source[1])})

    gf = pgv.AGraph(directed=True, strict=False)
    graph_opt = {
        "format": 'png',
        "dpi": 300,
        # "ranksep": 1,
        # "rankdir": "LR",
        # "splines": "polyline"
        "bgcolor": "transparent",
    }

    node_opt = {
        "style": "filled",
        "fontname": "IBM Plex Sans",
        "fillcolor": p.ultramarine(shade=25)
    }
    gf.edge_attr['len'] = 5

    for k, v in graph_opt.items():
        gf.graph_attr[k] = v

    for k, v in node_opt.items():
        gf.node_attr[k] = v

    mx = max([x[1] for x in cn.most_common()])

    for c in cn.most_common():
        label = "".join([str(x) for x in c[0]])
        pw = c[1] / mx
        if c[0][2] == 0:
            gf.add_edge(c[0][0], c[0][1], arrowhead="dot",
                        label=f"{c[1]}",
                        color=p.red(shade=10 + 60 * pw))
        else:
            gf.add_edge(c[0][0], c[0][1],
                        label=f"{c[1]}",
                        color=p.gray(shade=10 + 60 * pw))

    gc = GraphAdjustment(gf)
    gc.filename = "plot.png"
    gc.change_label(0, "Nkx2.5")
    gc.highlight(0, p.green_light(shade=40))
    gc.draw()


def check_steady_state_frequency(network):
    p = Palette()
    na = NetworkAnalyser(5, 4)
    similar = get_similar(network)
    all_ss = []
    all_len = []
    for s in similar:
        ss = list(na.get_attractors(na.get_state_space(s)))
        all_len.append(len(ss))
        len_mat = [len(x) for x in ss]
        if len(set(len_mat)) != 1:
            print("Oscillations ======")
        ss = [list(x)[0] for x in ss]
        all_ss.append(ss)

    cn = Counter()
    for s in all_ss:
        for km in s:
            cn.update({km})

    values = []
    labels = []
    for c in cn.most_common():
        values.append(c[1])
        labels.append(c[0])

    colors = [p.ultramarine(shade=40)] * len(values)
    colors[0] = p.green(shade=40)
    colors[1] = p.green(shade=40)
    plt.barh(range(len(values)), values, color=colors)
    plt.yticks(range(len(values)), labels, fontsize=8)
    plt.gca().invert_yaxis()
    plt.gca().set_facecolor(p.gray(shade=15))
    plt.grid(axis="x", ls=":")
    plt.xlabel("Number of times steady state appeared")
    plt.savefig("plot.png", dpi=300)
    plt.show()


def _node_match(n1, n2):
    try:
        return n1["gate"] == n2["gate"]
    except KeyError:
        return True


def isomorph():
    graph = nx.MultiDiGraph()
    graph.add_node(1, gate=1)
    graph.add_edge(1, 3)
    graph.add_edge(4, 5)
    graph.add_edge(2, 1)

    graph2 = nx.MultiDiGraph()
    graph2.add_node(10, gate=0)
    graph2.add_edge(10, 2)
    graph2.add_edge(30, 4)
    graph2.add_edge(1, 10)

    print(nx.is_isomorphic(graph, graph2, node_match=_node_match))


def run():
    # extract_networks()
    # network = {1: [1, [[0, 1], [3, 1]]], 2: [1, [[0, 1], [4, 1]]]}
    # na = NetworkAnalyser(5, 4)
    isomorph()
