#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
# All classes and objects related to Network will go here

import itertools
from collections import OrderedDict
from typing import Dict

from BooleanTRN.models.logic import *


class Network:
    def __init__(self, data):
        self.data = data  # type: Dict[str, LogOp]
        self._nodes = None

    @property
    def nodes(self) -> Dict[str, Variable]:
        if self._nodes is None:
            all_vars = []
            for items in self.data.values():
                if isinstance(items, Variable):
                    if items not in all_vars:
                        all_vars.append(items)
                else:
                    for m in items.get_variables():
                        if m not in all_vars:
                            all_vars.append(m)
            # Just use ordered OrderDict as a fail safe
            self._nodes = OrderedDict({x.name: x for x in all_vars})
        return self._nodes

    def print_network(self):
        for key, item in self.data.items():
            print(f"{key} := {item}")

    def _reset_variables(self):
        for n in self.nodes.values():
            n.reset()

    @property
    def steady_states(self):
        states = []
        while True:
            tmp = [x.state for x in self.data.values()]
            if states:
                if tmp in states:
                    oscillations = tmp != states[-1]
                    os_ind = states.index(tmp)
                    break

            states.append(tmp)
            updated_values = {}
            for key in self.data:
                if key in self.nodes:
                    updated_values[key] = self.data[key].state

            for key in updated_values:
                self.nodes[key].state = updated_values[key]

        self._reset_variables()
        if oscillations:
            return states[os_ind:]
        else:
            return [states[-1]]

    def find_states(self):
        states = []

        def _convert(items):
            return "".join([str(int(s)) for s in items])

        tmp = itertools.repeat([True, False], len(self.nodes))
        for x in itertools.product(*tmp):
            for i, key in enumerate(self.nodes):
                self.nodes[key].state = x[i]

            states.append((_convert(x), "/".join([_convert(x) for x in
                                                  self.steady_states])))

        print(f"Nodes : {list(self.nodes.keys())}")
        print(f"Steady State : {list(self.data.keys())}")
        print("Nodes State -> Steady State")
        for k in states:
            print(f"{k[0]} -> {k[1]}")


def run():
    a = Variable("a", True)
    b = Variable("b", True)
    c = Variable("c", False)

    data = {"a": OR(a, c), "b": NOT(b)}
    n = Network(data)
    n.find_states()
