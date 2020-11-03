#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
#  Main NetworkAnalyser class and realted functions

import itertools as itr
from typing import Union

import networkx as nx

GATE_AND = 0
GATE_OR = 1
INTERACTION_POSITIVE = 1
INTERACTION_NEGATIVE = 0


class ConEdge:
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
        self.interaction = None

    def get(self):
        return self.source, self.destination, self.interaction

    def __repr__(self):
        return f"Edge({self.source}, {self.destination}, {self.interaction})"


class ConNode:
    def __init__(self, name: int):
        self.name = name
        self.inputs = []
        self.gate = None

    def add_input(self, value: tuple):
        self.inputs.append(value)

    def add_gate(self, value: int):
        self.gate = value

    def get(self):
        return self.gate, self.inputs

    def __repr__(self):
        return f"Node({self.name})"


class NetworkAnalyser:
    def __init__(self, no_of_nodes: int,
                 no_of_edges: int,
                 *,
                 gates=None,
                 interactions=None,
                 is_connected: bool = False,
                 allow_negative: bool = False):
        if gates is None:
            gates = [GATE_OR]
        if interactions is None:
            interactions = [INTERACTION_POSITIVE]
            if allow_negative:
                interactions.append(INTERACTION_NEGATIVE)
        self.no_of_nodes = no_of_nodes
        self.no_of_edges = no_of_edges
        self.is_connected = is_connected
        self.gates = gates
        self.interaction = interactions

    def _get_pairs(self):
        possible = itr.product(range(self.no_of_nodes),
                               range(self.no_of_nodes))
        comb = itr.combinations(possible, self.no_of_edges)
        for c in comb:
            tmp = [ConEdge(*x) for x in c]
            yield tuple(tmp)

    def _should_skip(self, single):
        # If we do not care about connectedness, we should not skip
        if not self.is_connected:
            return False

        # Check if network is connected
        graph = nx.Graph()
        for n in single:
            graph.add_edge(n[0], n[1])
        return not (nx.is_connected(graph) and len(graph.nodes) ==
                    self.no_of_nodes)

    def _make_raw_network(self, network):
        for n in network:
            if self._should_skip(n):
                continue
            tmp = {}
            for k in n:
                if k[1] in tmp:
                    tmp[k[1]].add_input((k[0], k[2]))
                else:
                    tmp[k[1]] = ConNode(k[1])
                    tmp[k[1]].add_input((k[0], k[2]))

            tmp = list(tmp.values())
            # Add gate information
            gts = itr.repeat(self.gates, len(tmp))
            for m in itr.product(*gts):
                for i in range(len(tmp)):
                    tmp[i].add_gate(m[i])
                rt = {x.name: x.get() for x in tmp}
                yield rt

    def _add_interactions(self, network):
        for n in network:
            tmp = itr.repeat(self.interaction, len(n))
            for act in itr.product(*tmp):
                for i in range(len(n)):
                    n[i].interaction = act[i]
                tmp = [x.get() for x in n]
                yield tuple(tmp)

    def _solve(self, network: dict, init: tuple) -> str:
        states = []
        for i in range(self.no_of_nodes):
            if i in network.keys():
                # Collect the expression states from inputs
                items = []
                for sub in network[i][1]:
                    if sub[1] == INTERACTION_POSITIVE:
                        items.append(init[sub[0]])
                    elif sub[1] == INTERACTION_NEGATIVE:
                        items.append(int(not bool(init[sub[0]])))
                    else:
                        raise ValueError(
                            f"Unknown interaction type {sub[1]}'. Only allowed"
                            f" interactions are {INTERACTION_POSITIVE}:"
                            f" Positive and {INTERACTION_NEGATIVE}: Negative")
                if network[i][0] == GATE_OR:
                    states.append(max(items))
                elif network[i][0] == GATE_AND:
                    states.append(min(items))
                else:
                    raise ValueError(
                        f"Unknown logic gate '{network[i][0]}'. Only allowed "
                        f"gates are {GATE_AND}: AND , {GATE_OR}: OR")
            else:
                states.append(init[i])
        return "".join([str(x) for x in states])

    def get_state_space(self, network: dict) -> dict:
        space = {}
        tmp = itr.repeat([1, 0], self.no_of_nodes)
        for init in itr.product(*tmp):
            start = "".join([str(x) for x in init])
            target = self._solve(network, init)
            if start not in space.keys():
                space[start] = target
        return space

    @staticmethod
    def get_attractors(state_space: dict) -> list:
        graph = nx.DiGraph()
        for key, value in state_space.items():
            graph.add_edge(key, value)
        return nx.attracting_components(graph)

    @staticmethod
    def print_raw_network(network):
        links = []
        for k in network:
            for s in network[k][1]:
                arrow = "->"
                if s[1] == INTERACTION_NEGATIVE:
                    arrow = "-|"
                item = f"{s[0]} {arrow} {k}"
                if network[k][0] == GATE_AND:
                    item += "*"
                links.append(item)
        links = sorted(links)
        print(", ".join(links))

    def _validate_targets(self, values: list):
        for v in values:
            if not isinstance(v, str):
                raise TypeError(
                    f"Target should be String, you have provided {type(v)}")
            if len(v.strip()) != self.no_of_nodes:
                raise ValueError(f"Target '{v}' should have same number of "
                                 f"characters as number of nodes (currently, "
                                 f"{self.no_of_nodes}) in the network.")

    def find_networks(self, targets: Union[str, list] = None,
                      strict: bool = False,
                      ignore_limit_cycles: bool = False,
                      ignore_steady_states: bool = False):

        if isinstance(targets, str):
            targets = [targets]
        if targets is not None:
            self._validate_targets(targets)

        pairs = self._get_pairs()
        acts = self._add_interactions(pairs)
        raw = self._make_raw_network(acts)

        for r in raw:
            # If target is not provided return everything
            if targets is None:
                yield r
            # If target is provided
            else:
                sp = self.get_state_space(r)
                ss = []
                lc = []
                for s in self.get_attractors(sp):
                    if len(s) == 1:
                        ss.append(list(s)[0])
                    else:
                        lc.extend(list(s))
                if strict:
                    used = False  # Needed to exhaust 'yeild'
                    if not ignore_steady_states and not used:
                        if all([x in ss for x in targets]):
                            used = True
                            yield r
                    if not ignore_limit_cycles and not used:
                        if all([x in lc for x in targets]):
                            yield r
                else:
                    used = False  # Needed to exhaust 'yield'
                    if not ignore_steady_states and not used:
                        if any([x in ss for x in targets]):
                            used = True
                            yield r
                    if not ignore_limit_cycles and not used:
                        if any([x in lc for x in targets]):
                            yield r


class RawNetwork:
    def __init__(self, data: dict):
        self.data = data
        self._nodes = None
        self._edges = None
        self._graph = None

    @property
    def nodes(self):
        if self._nodes is None:
            self._make()
        return self._nodes

    @property
    def edges(self):
        if self._edges is None:
            self._make()
        return self._edges

    def _make(self):
        self._nodes = []
        self._edges = []
        for des, value in self.data.items():
            if des not in self._nodes:
                self._nodes.append(des)
            for action in value[1]:
                if action[0] not in self._nodes:
                    self._nodes.append(action[0])
                self._edges.append((action[0], des, action[1]))

    def network(self) -> nx.DiGraph:
        if self._graph is not None:
            return self._graph
        graph = nx.DiGraph()
        for e in self.edges:
            graph.add_edge(e[0], e[1])
        self._graph = graph
        return self._graph
