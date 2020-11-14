#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
#
#  This file is part of BooleanTRN project.
#  All functions related to plotting will go here

import pygraphviz as pgv
from SecretColors import Palette
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
    for key, value in node_opt.items():
        d.node_attr[key] = value
    for key, value in edge_opt.items():
        d.edge_attr[key] = value
    for row, value in data.items():
        d.add_edge(row, value)

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

        if row[3] == GATE_AND:
            d.get_node(row[1]).attr['fillcolor'] = p.ultramarine()

    d.layout(layout)
    d.draw(filename)
    return d
