#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#

import math
import matplotlib.pyplot as plt
import networkx as nx
from SecretColors import Palette

from BooleanTRN.models.sweeps import NetworkAnalyser, RawNetwork


def draw_possible_networks(networks):
    p = Palette()
    data = []
    for n in networks:
        data.append(RawNetwork(n))

    columns = math.ceil(math.sqrt(len(data)))
    fig = plt.figure(figsize=(8, 8))
    for i, d in enumerate(data):
        ax = plt.subplot(columns, columns, i + 1,
                         frameon=True)  # type:plt.Axes
        ax.margins(0.5)
        graph = d.network()
        colors = []
        for n in graph.nodes:
            colors.append(p.blue(shade=40))
        nx.draw_networkx(graph,
                         ax=ax,
                         node_color=colors,
                         with_labels=False)

    plt.savefig("plot.png", dpi=300)
    plt.show()


def run():
    na = NetworkAnalyser(5, 1)
    draw_possible_networks(na.find_networks())
