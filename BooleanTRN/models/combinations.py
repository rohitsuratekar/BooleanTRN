#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#  All classes related to combinations

import itertools as itr
from collections import defaultdict

import networkx as nx

from BooleanTRN.helpers.constants import *


class _NetEdge:
    def __init__(self, start, end, interaction=None):
        self.start = start
        self.end = end
        self.interaction = interaction

    def get(self):
        return self.start, self.end, self.interaction

    def __repr__(self):
        return f"NE{self.start, self.end, self.interaction}"


class NetworkCombinations:

    def __init__(self, no_of_nodes: int,
                 no_of_edges: int,
                 only_connected=False,
                 gates=None,
                 interactions: list = None):
        if interactions is None:
            interactions = [INTERACTION_POSITIVE]
        if gates is None:
            gates = [GATE_OR]
        self.no_of_nodes = no_of_nodes
        self.no_of_edges = no_of_edges
        self.is_connected = only_connected
        self.interactions = interactions
        self.gates = gates
        self._default_solving_gate = GATE_OR

    def _get_pairs(self):
        possible = itr.product(range(self.no_of_nodes),
                               range(self.no_of_nodes))
        comb = itr.combinations(possible, self.no_of_edges)
        for c in comb:
            tmp = [_NetEdge(*x) for x in c]
            yield tuple(tmp)

    def _add_interactions(self, network):
        for n in network:
            tmp = itr.repeat(self.interactions, len(n))
            for act in itr.product(*tmp):
                for i in range(len(n)):
                    n[i].interaction = act[i]
                tmp = [x.get() for x in n]
                yield tuple(tmp)

    def _is_connected(self, graph):
        quick = set([y for x in graph for y in x[:2]])
        if len(quick) != self.no_of_nodes:
            return False
        g = nx.Graph()
        for n in graph:
            g.add_edge(n[0], n[1])
        return nx.is_connected(g) and len(g.nodes) == self.no_of_nodes

    def _add_gate(self, network):
        source = defaultdict(list)
        list(map(lambda x: source[x[1]].append(x[0]), network))
        source = [x for x in source.keys() if len(source[x]) > 1]
        gts = itr.repeat(self.gates, len(source))
        for g in itr.product(*gts):
            tmp = []
            for n in network:
                if n[1] in source:
                    tmp.append((*n, g[source.index(n[1])]))
                else:
                    tmp.append((*n, None))
            yield tmp

    def get_combinations(self):
        n = self._get_pairs()
        n = self._add_interactions(n)
        for m in n:
            if self.is_connected:
                if not self._is_connected(m):
                    continue
            for k in self._add_gate(m):
                yield k

    @staticmethod
    def _input_network(network):
        tmp = defaultdict(list)
        for n in network:
            tmp[n[1]].append((n[0], n[2], n[3]))
        return dict(tmp)

    def _solve(self, input_net, init):
        tmp = []
        for i in range(self.no_of_nodes):
            if i not in input_net.keys():
                tmp.append(init[i])
            else:
                gate = list(set([x[2] for x in input_net[i]]))
                if len(gate) != 1:
                    raise AttributeError(
                        "Gate assignment error. Please check Gate "
                        "implementation.")
                gate = gate[0] or self._default_solving_gate
                truth = []
                for t in input_net[i]:
                    if t[1] == INTERACTION_POSITIVE:
                        truth.append(init[0])
                    elif t[1] == INTERACTION_NEGATIVE:
                        truth.append(not init[0])
                    else:
                        raise AttributeError(
                            f"{t[i]} is an invalid interaction "
                            f"code. Available codes are : "
                            f"{INTERACTION_POSITIVE} and "
                            f"{INTERACTION_NEGATIVE}")
                if gate == GATE_OR:
                    tmp.append(int(any(truth)))
                elif gate == GATE_AND:
                    tmp.append(int(all(truth)))
                else:
                    raise AttributeError(f"{gate} is an invalid Gate code. "
                                         f"Available codes are: {GATE_OR}, "
                                         f"{GATE_AND}")

        return tuple(tmp)

    def get_state_space(self, network: list):
        net = self._input_network(network)
        tmp = itr.repeat([1, 0], self.no_of_nodes)
        state = {}
        for init in itr.product(*tmp):
            future = self._solve(net, init)
            future = [f"{int(x)}" for x in future]
            init = [f"{int(x)}" for x in init]
            state["".join(init)] = "".join(future)
        return state

    @staticmethod
    def find_attracting_components(network: dict):
        graph = nx.DiGraph()
        for key, value in network.items():
            graph.add_edge(key, value)
        ss = []
        oc = []
        for n in nx.attracting_components(graph):
            if len(n) == 1:
                ss.append(list(n)[0])
            else:
                oc.append(list(n))
        del graph
        return ss, oc

    def find(self, target: list = None,
             strict: bool = True,
             ignore_oscillations: bool = False,
             show_progress: bool = False,
             ignore_steady_states: bool = False):
        if target is not None:
            for t in target:
                if len(t.strip()) != self.no_of_nodes:
                    raise ValueError(f"Invalid target '{t}'. It should have "
                                     f"exactly same number of characters as "
                                     f"number of nodes {self.no_of_nodes}")
                if not set(list(t)).issubset({"1", "0"}):
                    raise ValueError(f"Invalid target '{t}'. Every character "
                                     f"of the target should be either 1 or 0.")

        nets = self.get_combinations()
        c = 0
        for n in nets:
            if show_progress:
                print(f"\rScanned Combinations: {c}", end="")
                c += 1
            if target is None:
                yield n
            else:
                state = self.get_state_space(n)
                ss, oc = self.find_attracting_components(state)
                all_oc = [y for x in oc for y in x]
                how = all
                if not strict:
                    how = any
                if not ignore_steady_states:
                    if how([x in ss for x in target]):
                        yield n
                        continue
                if not ignore_oscillations:
                    if how([x in all_oc for x in target]):
                        yield n
                        continue
