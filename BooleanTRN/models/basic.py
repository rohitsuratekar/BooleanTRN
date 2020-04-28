#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
#  All basic models

from collections import defaultdict
from typing import Iterator


class Node:
    def __init__(self, name: str, expression: bool = False):
        self.name = name.strip()
        self.expression = expression

    def __repr__(self):
        return f"({self.name}, {int(self.expression)})"


class Graph:
    def __init__(self):
        self._nodes = defaultdict(list)
        self._initial_condition = None
        self._all_nodes = []
        self._current_expression = None
        self._history = defaultdict(list)
        self._unique_expression = None
        self._time = 0
        # Last element in history will be the current expression

    @property
    def all_nodes(self) -> list:
        return self._all_nodes

    @property
    def initial_conditions(self) -> dict:
        if self._initial_condition is None:
            raise ValueError("Please set initial conditions to continue.")
        return self._initial_condition

    @property
    def expression(self) -> dict:
        return self._current_expression

    @property
    def history(self) -> dict:
        return self._history

    def _validate(self, node: str):
        if node not in self.all_nodes:
            raise KeyError(f"'{node}' not found in current graph.")

    def get_inputs(self, node: str) -> list:
        """Returns names of unique nodes which are are giving input on the
        current node. This will not enlist multiple edges arising from the
        same node.

        :param node: Name of the node (Case Sensitive)
        :return: List of unique inputs
        """
        self._validate(node)
        return list(set([x[0] for x in self._nodes[node]]))

    def get_node(self, node: str) -> list:
        """Returns inputs to current node with all meta data
        :param node: Name of the node (Case Sensitive)
        :return: List of inputs
        """
        self._validate(node)
        return self._nodes[node]

    def make_from_data(self, data: Iterator) -> None:
        """
        Takes data and converts into the graph. Each element of the iterator
        should contains at least 3 items. with following sequence.
        [Origin Node:str, Destination Node:str, Interaction Type:int, ...]

        :param data: Data for generation of graph
        :return: None
        """
        temp = []
        for item in data:
            n1, n2, n3 = item[0], item[1], item[2:]
            temp.extend([n1, n2])
            if n1 not in self._nodes[n2]:
                self._nodes[n2].append((n1, *n3))

        # Create list of all nodes
        self._all_nodes = list(set(temp))

    def set_initial_condition(self,
                              conditions: dict,
                              fill_default: bool = None):
        # Find out which components are not included in the given initial
        # conditions.
        missing = list(set(self.all_nodes) - set(conditions.keys()))

        if fill_default is None:
            # To avoid accidental missing of any element, check if all the
            # nodes are present in the given initial conditions
            if set(conditions.keys()) != set(self.all_nodes):
                raise KeyError(
                    f"Initial conditions should have exactly same set "
                    f"of keys as nodes in the graph. Following nodes "
                    f"are missing from the initial conditions : "
                    f"{missing}. "
                    f"You can set 'fill_default=True' option if you "
                    f"want to set rest of the nodes to True")
        else:
            for elem in missing:
                conditions[elem] = fill_default

        # Set the initial conditions in all related variables
        self._initial_condition = conditions
        self._current_expression = conditions
        self._update_history(conditions)

    def _update_history(self, conditions):
        for c in conditions:
            self._history[c].append(conditions[c])

        self._time += 1

    def _is_unique(self) -> bool:
        if self._unique_expression is None:
            self._unique_expression = []

        temp = "".join([str(int(self._current_expression[x])) for x in
                        self.all_nodes])

        if temp in self._unique_expression:
            return False
        else:
            self._unique_expression.append(temp)

        return True

    def update(self, steps: int = 1):
        for _ in range(steps):
            # Is expression pattern exists, stop the iteration
            if not self._is_unique():
                return
            new_state = {}
            for node in self.all_nodes:
                ns = self.get_node(node)
                if len(ns) == 0:
                    # If there is no input, carry forward current state
                    new_state[node] = self._current_expression[node]
                else:
                    temp = []
                    for n in ns:
                        if n[1] == 1:
                            # Positive interaction
                            temp.append(self._current_expression[n[0]])
                        elif n[1] == 0:
                            # Negative interaction
                            temp.append(not self._current_expression[n[0]])
                        else:
                            raise ValueError(f"Interaction type {n[1]} is "
                                             f"not defined yet")

                    # OR gate on all the inputs
                    # TODO: Implement other fine logic in future if needed
                    new_state[node] = max(temp)

            # Update all records
            self._current_expression = new_state
            self._update_history(new_state)

    def print(self):
        for node in self._nodes:
            for elem in self.get_node(node):
                arrow = "->"
                if elem[1] == 0:
                    arrow = "-|"
                print(f"{elem[0]} {arrow} {node}")

    def print_history(self):
        print(f" \t   {[x for x in range(self._time)]}")
        for h in self.history:
            print(f"{h} \t-> {[int(x) for x in self.history[h]]}")
