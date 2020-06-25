#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
# All graphics related classes

from SecretColors import Palette
from SecretPlots import NetworkPlot

from BooleanTRN.models.network import Network


def draw_state_space(network: Network):
    p = Palette()
    data = []
    nodes = []
    c_mapping = {}
    for n in network.find_states():
        node = f"start_{n[0]}"
        tmp = [node]
        nodes.append(node)
        c_mapping[node] = p.gray()
        tmp.extend(n[1])
        for i in range(0, len(tmp) - 1):
            data.append([tmp[i], tmp[i + 1], 1])

    n = NetworkPlot(data)
    n.node_placement = nodes
    n.colors_mapping = c_mapping
    n.max_columns = 4
    n.show()


def run():
    pass
