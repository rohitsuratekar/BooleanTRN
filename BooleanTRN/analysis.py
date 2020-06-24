#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
# Bottom up approach

from collections import defaultdict
from BooleanTRN.models.logic import *


class NetworkAnalysis:
    def __init__(self, data, initial_state):
        self.data = data
        self._nodes = None
        self._current_state = None
        self._history = None
        self._initial_state = initial_state

    @property
    def nodes(self) -> dict:
        if self._nodes is None:
            self._nodes = {}
            temp = list(set([y for x in self.data for y in x[:2]]))
            for t in temp:
                try:
                    self._nodes[t] = Variable(t, self.current_state[t], True)
                except KeyError as k:
                    raise KeyError(f"You have not provided initial "
                                   f"condition for '{t}'") from k
        return self._nodes

    @property
    def current_state(self) -> dict:
        if self._current_state is None:
            self._current_state = {}
            for key, item in self._initial_state:
                self._current_state[key] = bool(item)
        return self._current_state

    def generate_network(self):
        pass


def run():
    data = [
        ["a", "b", 1],
        ["b", "c", 1],
        ["g", "a", 1]
    ]
    initial_state = [
        ["a", 1],
        ["b", 0],
        ["c", 1],
        ["g", 1]
    ]
    a = Variable("a", True, True)
    b = Variable("b", True, True)
    c = Variable("c", False, True)
    d = Variable("d", True, True)

    net = {"a": OR(a, b), "b": OR(c, d)}
    n = NetworkAnalysis(data, initial_state)

    print(n.nodes)
