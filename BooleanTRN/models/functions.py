#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#

from typing import List, Tuple
from collections import defaultdict
import itertools


class Edge:
    """
    Simple data holder class.
    """

    def __init__(self, data):
        self.data = data
        self.origin = data[0].strip()
        self.destination = data[1].strip()
        self.type = data[2]
        self.is_positive = self.type == 1


def _convert_to_str(sl: tuple):
    return "".join([str(x) for x in sl])


def _solve_network(data: List[Edge], nodes: List[str],
                   initial_conditions: tuple,
                   gate: str) -> tuple:
    tmp = defaultdict(list)
    for d in data:
        idx = nodes.index(d.origin)
        if d.is_positive:
            tmp[d.destination].append(initial_conditions[idx])
        else:
            tmp[d.destination].append(int(not initial_conditions[idx]))

    final_states = []
    for n in nodes:
        if n in tmp.keys():
            # Important to decide which logic gate you want to use
            if gate == "OR":
                final_states.append(max(tmp[n]))  # Max == OR gates
            else:
                final_states.append(min(tmp[n]))  # Min == AND gate
        else:
            final_states.append(initial_conditions[nodes.index(n)])

    return tuple(final_states)


def _get_redundant(data: list) -> list:
    source_nodes = set([x[0] for x in data])
    sink_nodes = set([x[1] for x in data])
    leaves = sink_nodes - source_nodes
    return list(leaves)


def generate_state_space(data: List[tuple], *, gate: str,
                         node_order: list = None,
                         remove_redundant: bool = False) -> Tuple[list,
                                                                  dict, list]:
    """
    Take network data in the form of list of (origin, destination, type) and
    generates state space for the given network.

    Type can be 1 (for positive interaction) or 0 (for negative interaction)

    Gate can be 'or' or 'and'

    :param data: List of tuples (origin, destination, type)
    :type data: List[tuple]
    :param gate: Default gate used for Boolean calculations
    :type gate: str
    :param remove_redundant: If True, leaves will be removed from the graph
    [default: False]
    :type remove_redundant: bool
    :param node_order: Decide your own custom node order
    :type node_order: list
    :return: Node Order, Dictionary of state space, List of redundant nodes
    :rtype: tuple
    """
    gate = gate.strip().upper()
    if gate not in ["OR", "AND"]:
        raise ValueError(f"'gate' can only be 'OR' or 'AND'. You have "
                         f"provided {gate}")

    redundant_nodes = []
    if remove_redundant:
        redundant_nodes = _get_redundant(data)

    # Generate the nodes
    nodes = [y for x in data for y in x[:2] if y not in redundant_nodes]
    nodes = sorted(set([x.strip() for x in nodes]))
    if node_order is not None:
        tmp_nodes = [x for x in node_order if x in nodes]
        for x in nodes:
            if x not in tmp_nodes:
                tmp_nodes.append(x)
        nodes = tmp_nodes
    # Make network from the data
    network = [Edge(x) for x in data]
    tmp = itertools.repeat([0, 1], len(nodes))
    state_space = {}
    # Generate the state space
    for x in itertools.product(*tmp):
        x_str = _convert_to_str(x)
        if x_str not in state_space.keys():
            state_space[x_str] = _convert_to_str(
                _solve_network(network, nodes, x, gate))
    return nodes, state_space, redundant_nodes
