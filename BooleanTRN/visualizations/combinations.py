#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#

import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from SecretColors import Palette

from BooleanTRN.models.sweeps import RawNetwork, NetworkAnalyser

np.random.seed(1989)


def draw_possible_networks(networks, only_take=None):
    p = Palette()
    data = []
    for n in networks:
        data.append(RawNetwork(n))

    print(len(data))
    if only_take is not None:
        data = np.random.choice(data, only_take)

    columns = math.ceil(math.sqrt(len(data)))
    fig = plt.figure(figsize=(11, 11))
    for i, d in enumerate(data):
        ax = plt.subplot(columns, columns, i + 1,
                         frameon=True)  # type:plt.Axes
        ax.margins(0.1)
        ax.set_facecolor(p.gray(shade=10))
        graph = d.network()
        colors = []
        for n in graph.nodes:
            colors.append(p.blue(shade=40))
        pos = nx.nx_agraph.graphviz_layout(graph)
        nx.draw_networkx(graph,
                         pos=pos,
                         ax=ax,
                         node_color=colors,
                         with_labels=False)

    plt.savefig("plot.png", dpi=300)
    plt.show()


def run():
    na = NetworkAnalyser(5, 4)
    na.is_connected = True
    draw_possible_networks(na.find_networks(), only_take=25)
