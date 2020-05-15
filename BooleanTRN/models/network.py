#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
# All network related models will go here

from typing import List, Dict

from BooleanTRN.models.basic import Variable


class Edge:
    def __init__(self, data):
        self.start = data[0]
        self.end = data[1]
        self.interaction = int(data[2])

    @property
    def is_positive(self) -> bool:
        return self.interaction == 1


class Node:
    def __init__(self, name: str, state: bool = True):
        self.name = name
        self._state = state
        self._variable = None

    @property
    def variable(self) -> Variable:
        if self._variable is None:
            self._variable = Variable(self.name, self._state)
        return self._variable

    @property
    def state(self) -> bool:
        return self.variable.state

    def update(self, value: bool):
        self._variable.state = value


class Graph:
    def __init__(self):
        self._nodes = None
        self._edges = None

    @property
    def nodes(self) -> Dict[str, Node]:
        return self._nodes

    @property
    def edges(self) -> List[Edge]:
        return self._edges

    def _generate_nodes(self, nd: str):
        if self._nodes is None:
            self._nodes = {}
        if nd not in self._nodes.keys():
            self._nodes[nd.strip()] = Node(nd.strip())

    def _generate_edge(self, data):
        if self._edges is None:
            self._edges = []
        self._edges.append(Edge(data))

    def _parse_data(self, data):
        for item in data:
            start, end, tp = item
            self._generate_nodes(start)
            self._generate_nodes(end)
            self._generate_edge(item)

    @classmethod
    def from_data(cls, data):
        d = cls()
        d._parse_data(data)
        return d

    def print_edges(self):
        for e in self.edges:
            arrow = "-->"
            if not e.is_positive:
                arrow = "--|"
            print(f"{e.start} {arrow} {e.end}")

    def print_nodes(self):
        for n in self.nodes.values():
            print(n.name)

    def update_states(self):
        for e in self.edges:
            print(e.start)


def run():
    data = [
        ["a", "b", 1],
        ["b", "c", 0]
    ]
    graph = Graph.from_data(data)
    graph.update_states()

