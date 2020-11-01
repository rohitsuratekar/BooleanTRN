#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#

import itertools as itr
from collections import defaultdict

import networkx as nx


def get_pairs(no_of_elements: int, no_of_links: int):
    possible = itr.product(range(no_of_elements), range(no_of_elements))
    comb = itr.combinations(possible, no_of_links)
    for c in comb:
        yield c


def make_network(no_of_elements: int, pairs):
    for m in pairs:
        current = defaultdict(list)
        for source, dest in m:
            current[dest].append(source)
        for i in range(no_of_elements):
            if i not in current:
                current[i].append(i)
        yield current


def add_gates(networks, gates):
    for n in networks:
        new_net = defaultdict(list)
        gt = itr.repeat(gates, len(n.keys()))
        order = list(n.keys())
        for cg in itr.product(*gt):
            for i, o in enumerate(order):
                new_net[o] = [(x, cg[i]) for x in n[o]]
            yield new_net


def get_state(network, initial_condition) -> str:
    state = ""
    for i in range(len(network)):
        inputs = [initial_condition[x[0]] for x in network[i]]
        if len(inputs) == 1:
            state += f"{inputs[0]}"
        else:
            gate = network[i][0][1]
            if gate == 0:
                # OR GATE
                state += f"{max(inputs)}"
            elif gate == 1:
                # AND GATE
                state += f"{min(inputs)}"
            else:
                raise ValueError(f"Unrecognized gate '{gate}'. Available "
                                 f"gates : OR (0) , AND (1)")
    return state


def find_attractors(states):
    graph = nx.DiGraph()
    for key, value in states.items():
        graph.add_edge(key, value)
    elm = [tuple(sorted(x)) for x in nx.attracting_components(graph)]
    del graph
    return tuple(sorted(elm))


def solve_networks(networks):
    for n in networks:
        space = {}
        init = itr.repeat([0, 1], len(n.keys()))
        for init_cond in itr.product(*init):
            i_space = "".join(map(str, init_cond))
            if i_space not in space:
                s_space = get_state(n, init_cond)
                space[i_space] = s_space

        sts = find_attractors(space)
        yield sts


def run():
    no_of_elements = 4
    no_of_links = 2
    pairs = get_pairs(no_of_elements, no_of_links)
    networks = make_network(no_of_elements, pairs)
    n_gates = add_gates(networks, [1, 0])
    ns = solve_networks(n_gates)

    for n in ns:
        print(n)
