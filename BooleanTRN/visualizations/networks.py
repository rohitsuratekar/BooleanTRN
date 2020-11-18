#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
#
#  This file is part of BooleanTRN project.
#  All functions related to plotting will go here

import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pygraphviz as pgv
from SecretColors import Palette
from BooleanTRN.helpers.constants import *
from BooleanTRN.helpers.constants import *


class GraphAdjustment:
    def __init__(self, graph: pgv.AGraph):
        self.graph = graph
        self.filename = "../plot.png"
        self.layout = "dot"
        self.palette = Palette()

    def node_to_text(self, node):
        self.graph.get_node(node).attr['shape'] = "plaintext"
        self.graph.get_node(node).attr['fillcolor'] = None

    def hide(self, node):
        self.graph.get_node(node).attr['style'] = "invis"
        for n in self.graph.edges():
            if node in n:
                self.graph.get_edge(*n).attr['style'] = "invis"

    def add_edge(self, data: tuple):
        self.graph.add_edge(data[0], data[1])
        self.graph.get_edge(data[0], data[1]).attr[
            'color'] = self.palette.ultramarine()

    def remove_edge(self, start_node, end_node):
        e = self.graph.get_edge(start_node, end_node)
        e.attr['style'] = 'dashed'
        e.attr['color'] = self.palette.red()

    def change_label(self, node, label):
        n = self.graph.get_node(node)
        n.attr['label'] = label

    def highlight(self, node_name, color=None):
        if color is None:
            color = self.palette.red(shade=30)
        self.graph.get_node(node_name).attr['fillcolor'] = color

    def mutant(self, node_name):
        node = self.graph.get_node(node_name)
        node.attr['fillcolor'] = self.palette.gray(shade=20)
        node.attr['color'] = "none"

        for e in self.graph.edges():
            if node_name in e:
                ed = self.graph.get_edge(*e)
                ed.attr['style'] = 'dashed'
                ed.attr['arrowType'] = 'none'
                ed.attr['color'] = self.palette.gray(shade=20)

    def draw(self):
        self.graph.layout(self.layout)
        self.graph.draw(self.filename)


def plot_transition_graph(data: dict,
                          layout: str = "neato",
                          *,
                          color_mapping: dict = None,
                          filename: str = "plot.png",
                          graph_opt: dict = None,
                          node_opt: dict = None,
                          edge_opt: dict = None):
    p = Palette()
    graph_opt = _concatenate(graph_opt, {
        "format": 'png',
        "dpi": 300,
        "directed": True,
        "bgcolor": "transparent",
        "start": "random2"
    })

    node_opt = _concatenate(node_opt, {
        "style": "filled",
        "fontname": "IBM Plex Sans",
        "fillcolor": p.gray(shade=15)
    })

    edge_opt = _concatenate(edge_opt, {
        "len": 1.2
    })

    d = pgv.AGraph(**graph_opt)
    graph = nx.MultiDiGraph()
    for key, value in node_opt.items():
        d.node_attr[key] = value
    for key, value in edge_opt.items():
        d.edge_attr[key] = value
    for row, value in data.items():
        d.add_edge(row, value)
        graph.add_edge(row, value)

    for con in nx.attracting_components(graph):
        if len(con) == 1:
            d.get_node(list(con)[0]).attr['fillcolor'] = p.green(shade=30)
        else:
            for c in list(con):
                d.get_node(c).attr['fillcolor'] = p.violet(shade=30)

    if color_mapping is not None:
        for key, value in color_mapping.items():
            d.get_node(key).attr["fillcolor"] = value

    d.layout(layout)
    d.draw(filename)
    return d


def _concatenate(opts, defaults):
    if opts is None:
        return defaults
    return {**defaults, **opts}


def plot_network(data, *, layout: str = "dot",
                 filename="plot.png",
                 graph_opt=None, node_opt=None, edge_opt=None):
    p = Palette()
    graph_opt = _concatenate(graph_opt, {
        "format": 'png',
        "dpi": 300,
        "directed": True,
        "bgcolor": "transparent"
    })

    node_opt = _concatenate(node_opt, {
        "style": "filled",
        "fontname": "IBM Plex Sans",
        "fillcolor": p.ultramarine(shade=25)
    })

    edge_opt = _concatenate(edge_opt, {
        "len": 1.2
    })

    d = pgv.AGraph(**graph_opt)
    for key, value in node_opt.items():
        d.node_attr[key] = value
    for key, value in edge_opt.items():
        d.edge_attr[key] = value
    for row in data:
        d.add_edge(row[0], row[1])
        if row[2] == INTERACTION_NEGATIVE:
            d.get_edge(row[0], row[1]).attr['arrowhead'] = "dot"
            d.get_edge(row[0], row[1]).attr['color'] = p.red(shade=40)

        if row[3] == GATE_AND:
            d.get_node(row[1]).attr['fillcolor'] = p.ultramarine()

    d.layout(layout)
    d.draw(filename)
    return d


def plot_multiple_networks(networks, seed=None,
                           figsize=None,
                           mark=None):
    p = Palette()
    np.random.seed(seed)

    columns = math.ceil(math.sqrt(len(networks)))
    row = columns
    if len(networks) < 3:
        row = 1
    if columns * columns >= len(networks) + columns:
        row -= 1
        if row == 0:
            row = 1
    if figsize is not None:
        plt.figure(figsize=figsize)
    for i, d in enumerate(networks):
        ax = plt.subplot(row, columns, i + 1,
                         frameon=True)  # type:plt.Axes
        ax.margins(0.2)

        graph = nx.MultiDiGraph()
        edge_map = {}
        node_map = {}
        for x in d:
            if x[1] != x[0]:
                node_map[x[1]] = x[3]
            edge_map[(x[0], x[1])] = x[2]
            graph.add_edge(x[0], x[1])
        colors = []
        edge_colors = []
        for n in graph.nodes:
            if n in node_map:
                if n == mark:
                    if node_map[n] == GATE_OR:
                        colors.append(p.yellow(shade=15))
                    else:
                        colors.append(p.yellow(shade=35))
                elif node_map[n] == GATE_OR:
                    colors.append(p.blue(shade=40))
                else:
                    colors.append(p.blue(shade=60))
            else:
                if n == mark:
                    colors.append(p.yellow(shade=15))
                else:
                    colors.append(p.blue(shade=40))
        for e in graph.edges:
            if edge_map[(e[0], e[1])] == INTERACTION_NEGATIVE:
                edge_colors.append(p.red(shade=40))
            else:
                edge_colors.append(p.black())

        pos = nx.nx_agraph.graphviz_layout(graph,
                                           prog="dot")
        nx.draw_networkx(graph,
                         pos=pos,
                         ax=ax,
                         edge_color=edge_colors,
                         node_color=colors,
                         with_labels=False)
        ax.set_facecolor(p.gray(shade=10))
    plt.tight_layout()
    plt.savefig("plot.png", dpi=300, transparent=False)
    plt.show()
