#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
# All analysis will be done here.

import numpy as np
import pandas as pd
from typing import List


class Condition:
    def __init__(self, name, possible_outputs: list = None):
        self.name = name
        self.possible_outputs = possible_outputs

    def remove(self, nodes):
        if self.possible_outputs is None:
            return nodes
        return [x for x in nodes if x not in self.possible_outputs]


class FindNetwork:
    def __init__(self, initial_condition: list, final_states: list):
        self._start = {x[0]: x[1] for x in initial_condition}
        self._end = {x[0]: x[1] for x in final_states}
        self._nodes = None
        self.allow_auto_feedback = False
        self._matrix = None
        self._conditions = []

    @property
    def nodes(self) -> list:
        if self._nodes is None:
            self._nodes = [x[0] for x in self._start]
        return self._nodes

    @property
    def matrix(self) -> pd.DataFrame:
        if self._matrix is None:
            nd = len(self.nodes)
            mat = np.zeros(nd * nd).reshape(nd, nd)

            mat = pd.DataFrame(data=mat, columns=self.nodes, index=self.nodes)
            mat = mat.astype("str")
            self._matrix = mat
        return self._matrix

    def add_condition(self, condition: Condition):
        self._conditions.append(condition)

    def start(self, node: str):
        return self._start[node]

    def target(self, node: str):
        return self._end[node]

    def print_targets(self):
        for x in self.nodes:
            print(f"{x} : {self.start(x)} -> {self.target(x)}")

    def _check_conditions(self):
        if not self.allow_auto_feedback:
            for n in self.nodes:
                self.matrix[n][n] = None
        for c in self._conditions:
            for out in c.remove(self.nodes):
                self.matrix[c.name][out] = None

    def _calculate(self, condition, solve):
        pass

    def _check_possibilities(self, node: str):
        idx = self.nodes.index(node)
        start = self.start(node)
        end = self.target(node)
        possible_inputs = []
        for n in self.nodes:
            if self.matrix[n][node] is not None:
                possible_inputs.append(n)
        if len(possible_inputs) == 0:
            return
        print(start, end)
        print(possible_inputs)
        print(self.matrix.iloc[idx:idx + 1])

    def state_matrix(self):
        self._check_conditions()
        self._check_possibilities("b")


def calculate(target: tuple, restrictions: List[tuple]):
    print(restrictions, target)


def run():
    start = [("a", True), ("b", True), ("c", True)]
    end = [("a", False), ("b", True), ("c", True)]
    # fn = FindNetwork(start, end)
    # fn.add_condition(Condition("c", None))
    # fn.state_matrix()

    target = (True, True)
    restrictions = [("a", True)]
    calculate(target, restrictions)

