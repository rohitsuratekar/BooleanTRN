#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#

import itertools as itr
from collections import defaultdict
from BooleanTRN.visualizations import *
import networkx as nx
import json
from collections import Counter


class NetworkAnalyser:
    def __init__(self, no_of_nodes: int, no_of_edges: int):
        self.no_of_nodes = no_of_nodes
        self.no_of_edges = no_of_edges
        self.gates = [0]
        self.connected = False

    def _get_pairs(self):
        possible = itr.product(range(self.no_of_nodes),
                               range(self.no_of_nodes))
        comb = itr.combinations(possible, self.no_of_edges)
        for c in comb:
            yield c

    def change_gates(self, new_value: list):
        self.gates = new_value

    def is_connected(self, network):
        g = nx.Graph()
        for n in network:
            for k in network[n]:
                g.add_edge(k, n)
        return nx.is_connected(g) and len(g.nodes) == self.no_of_nodes

    def _make_network(self, pairs):
        for m in pairs:
            current = defaultdict(list)
            for source, dest in m:
                current[dest].append(source)

            if self.connected:
                if not self.is_connected(current):
                    continue
            for i in range(self.no_of_nodes):
                if i not in current:
                    current[i].append(i)
            yield current

    def _add_gates(self, networks):
        for n in networks:
            new_net = defaultdict(list)
            gt = itr.repeat(self.gates, len(n.keys()))
            order = list(n.keys())
            for cg in itr.product(*gt):
                for i, o in enumerate(order):
                    new_net[o] = [(x, cg[i]) for x in n[o]]
                yield new_net

    @staticmethod
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

    @staticmethod
    def find_attractors(states):
        graph = nx.DiGraph()
        for key, value in states.items():
            graph.add_edge(key, value)
        elm = [tuple(sorted(x)) for x in nx.attracting_components(graph)]
        del graph
        return tuple(sorted(elm))

    def _solve_networks(self, networks, target=None):
        for n in networks:
            space = {}
            init = itr.repeat([0, 1], len(n.keys()))
            for init_cond in itr.product(*init):
                i_space = "".join(map(str, init_cond))
                if i_space not in space:
                    s_space = self.get_state(n, init_cond)
                    space[i_space] = s_space
            sts = self.find_attractors(space)
            if target is None:
                yield n
            else:
                if set(target).issubset(sts):
                    yield n

    def _extract_networks(self):
        pairs = self._get_pairs()
        networks = self._make_network(pairs)
        return self._add_gates(networks)

    def _validate_ss(self, value):
        if len(value.strip()) != self.no_of_nodes:
            raise ValueError(f"Number of characters in the steady state '"
                             f"{value}' should be equal to number of nodes "
                             f"in the network '{self.no_of_nodes}'")

    def find_at_least(self, value: str):
        self._validate_ss(value)
        target = tuple([value.strip()])
        nts = self._extract_networks()
        for n in self._solve_networks(nts, [target]):
            yield dict(n)

    def find_multiple(self, values: list):
        [self._validate_ss(x) for x in values]
        targets = [tuple([x]) for x in values]
        nts = self._extract_networks()
        for n in self._solve_networks(nts, targets):
            yield dict(n)

    def analyse(self):
        n_gates = self._extract_networks()
        ns = self._solve_networks(n_gates)
        for n in ns:
            yield dict(n)

    @staticmethod
    def print_networks(nets):
        for n in nets:
            sp = defaultdict(list)
            full = []
            for des in n:
                for s in n[des]:
                    sp[s[0]].append(des)
            for s in sp:
                for des in sp[s]:
                    if s != des:
                        full.append(f"{s}->{des}")
            print(", ".join(sorted(full)))


def convert_to_dest(network):
    tmp = []
    for n in network:
        for des in network[n]:
            # Remove auto links
            if des[0] != n:
                tmp.append((des[0], n, 1))
    return tmp


def test_network(network):
    tmp = itr.repeat([1, 0], len(network))
    state = {}
    for t in itr.product(*tmp):
        i_space = "".join(map(str, t))
        st = NetworkAnalyser.get_state(network, t)
        if i_space not in state.keys():
            state[i_space] = st

    des_net = convert_to_dest(network)
    ga = GraphAdjustment(plot_network(des_net))
    ga.highlight(4)
    ga.draw()
    plot_transition_graph(state, filename="plot2.png")


def remove_isomorphic(network):
    graphs = []
    nets = []
    for n in network:
        g = nx.Graph()
        for des in n:
            for s in n[des]:
                # Remove auto-links
                if s[0] != des:
                    g.add_edge(s[0], des)

        if len(graphs) == 0:
            graphs.append(g)
            nets.append(n)
        else:
            if not any([nx.is_isomorphic(x, g) for x in graphs]):
                graphs.append(g)
                nets.append(n)

    del graphs
    return nets


def save_network(networks):
    son = {}
    counter = 0
    for n in networks:
        son[counter] = n
        counter += 1
    with open("networks.json", "w") as f:
        json.dump(son, f)


def load_network():
    with open("networks.json") as f:
        mk = json.load(f)
    con = []
    for m in mk.values():
        tmp = {}
        for k in m:
            tmp[int(k)] = [tuple(x) for x in m[k]]
        con.append(tmp)
    return con


def flow_diagram(networks):
    cn = Counter()
    for n in networks:
        for des in n:
            for sor in n[des]:
                # Remove auto link
                if sor[0] != des:
                    cn.update({(sor[0], des)})

    data = []
    for c in cn.most_common():
        data.append(c)

    g = network_flow_diagram(data, graph_opt={"bgcolor": "#ffffff"})
    ga = GraphAdjustment(g)
    ga.highlight(0)
    ga.change_label(0, "nkx2.5")
    ga.draw()


def search_graphs():
    na = NetworkAnalyser(5, 4)
    na.connected = True
    nts = na.find_multiple(["11111", "01111"])
    graphs = remove_isomorphic(nts)
    print(len(graphs))
    save_network(graphs)


def analyse_graphs():
    nts = load_network()
    flow_diagram(nts)


def run():
    # analyse_graphs()
    search_graphs()
