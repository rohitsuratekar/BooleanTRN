#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#  Analysis related to the finding network structures from the combination
#  of networks derived from this analysis

import math
from BooleanTRN.models.combinations import NetworkCombinations
import matplotlib.pyplot as plt
from SecretColors import Palette
import matplotlib
from matplotlib.patches import Patch
from matplotlib import ticker

matplotlib.rc("font", family="IBM Plex Sans")


def permutations(n, r):
    try:
        return math.factorial(n) / math.factorial(n - r)
    except ValueError:
        return 0


@ticker.FuncFormatter
def major_formatter(x, pos):
    return f'{x / 10000}'


def plot_combination_stat(nodes: int, edges: int, add_connected: bool = False):
    p = Palette()

    def __count(n: NetworkCombinations):
        c = 0
        for _ in n.find():
            c += 1
        return c

    values = []
    labels = []
    connected = []
    nc = NetworkCombinations(nodes, edges)

    pairs = permutations(nodes, 2) + nodes
    interactions = permutations(pairs, edges) / math.factorial(edges)

    # 1 interaction, 1 gate
    values.append(interactions)
    if add_connected:
        nc.is_connected = True
        connected.append(__count(nc))
        nc.is_connected = False
    labels.append((1, 1))

    # 1 interaction, 2 gates
    nc.gates = [0, 1]
    values.append(__count(nc))
    if add_connected:
        nc.is_connected = True
        connected.append(__count(nc))
        nc.is_connected = False
    labels.append((1, 2))

    # 2 interaction, 1 gate
    values.append(values[0] * pow(2, edges))
    if add_connected:
        connected.append(connected[0] * pow(2, edges))
    labels.append((2, 1))

    # 2 interactions, 2 gates
    values.append(values[1] * pow(2, edges))
    if add_connected:
        connected.append(connected[1] * pow(2, edges))
    labels.append((2, 2))

    plt.barh(range(len(values)), values, color=p.blue(), zorder=4)
    if add_connected:
        plt.barh(range(len(connected)), connected,
                 color=p.green(shade=30), zorder=5)
    labels = [f"IT:{x[0]}, GT:{x[1]}" for x in labels]
    plt.yticks(range(len(labels)), labels)

    if add_connected:
        handles = [
            Patch(color=p.blue(), label="All"),
            Patch(color=p.green(shade=30), label="Connected"),
        ]
        plt.legend(handles=handles, loc="center right")

    # plt.xscale("log")
    ax = plt.gca()  # type:plt.Axes
    ax.xaxis.set_major_formatter(major_formatter)
    ax.set_facecolor(p.gray(shade=15))
    for k, spine in ax.spines.items():
        spine.set_zorder(10)
    plt.grid(axis="x", color=p.gray(shade=40), ls=":", zorder=0)
    plt.annotate("IT: Interactions, GT: Gate",
                 xy=(0.99, 0.02), ha="right", va="bottom",
                 xycoords="axes fraction")
    plt.xlabel("Possible Combinations (x$10^4$)", labelpad=5)
    plt.title(f"Nodes: {nodes}, Edges: {edges}")
    plt.tight_layout()
    plt.savefig("plot.png", dpi=300)
    plt.show()


def run():
    plot_combination_stat(5, 4, add_connected=True)
