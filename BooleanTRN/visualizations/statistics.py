#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
#  All statistics visualizations

import csv
from collections import defaultdict
from multiprocessing import Process, Queue

import math
import matplotlib
import matplotlib.pylab as plt
from SecretColors import Palette

from BooleanTRN.models.sweeps import NetworkAnalyser

matplotlib.rc("font", family="IBM Plex Sans")


# 5p1

def cal_comb(q, network: NetworkAnalyser, analysis_id=0):
    c = 0
    for _ in network.find_networks():
        c += 1
    q.put((network.no_of_nodes, network.no_of_edges, c, analysis_id))


def generate_combinations():
    q = Queue()
    actions = 8
    all_process = []
    for j in range(1, actions):
        na = NetworkAnalyser(5, j)
        # na.gates = [1, 0]
        na.is_connected = True
        p = Process(target=cal_comb, args=(q, na, 5))
        p.start()
        all_process.append(p)

    data = []
    for _ in all_process:
        data.append(q.get())
        print(data[-1])

    with open("out.csv", "w") as f:
        print("nodes,edges,combinations,id", file=f)
        for d in data:
            print(",".join([str(x) for x in d]), file=f)

    print("Finished")


def plot_single_node(no_of_nodes):
    p = Palette()
    all_values = defaultdict(list)
    with open("data/five_nodes.csv") as f:
        next(f)
        for row in csv.reader(f):
            if int(row[0]) == int(no_of_nodes):
                all_values[int(row[3])].append((int(row[1]), int(row[2])))

    all_colors = [p.green(shade=60),
                  p.ultramarine(),
                  p.green(shade=50),
                  p.green(shade=40),
                  p.green(shade=30),
                  ]
    type_ids = ["2 types + 2 gates",
                "2 types + 2 gates (connected)",
                "2 types + 1 gate",
                "1 type + 2 gates",
                "1 type + 1 gate",
                ]

    for key, color, name in zip([3, 4, 1, 2, 0], all_colors, type_ids):
        actions = all_values[key]
        actions = sorted(actions, key=lambda x: x[0])
        values = [x[1] for x in actions]
        actions = [x[0] for x in actions]
        plt.bar(range(min(actions), max(actions) + 1), values,
                color=color, label=name, zorder=4)

    plt.yscale("log")
    plt.legend(loc=0)
    plt.xlabel("Number of Interactions")
    plt.ylabel("Possible Networks")
    plt.title(f"Number of nodes: {no_of_nodes}")
    plt.gca().set_facecolor(p.gray(shade=15))
    plt.grid(axis="y", ls=":", zorder=1)
    plt.savefig("plot.png", dpi=300)
    plt.show()


def plot_combinations():
    p = Palette()
    dm = defaultdict(list)
    with open("data/single_connected.csv") as f:
        next(f)
        data = csv.reader(f)
        for row in data:
            dm[row[1]].append((row[0], row[2]))

    mx_f = max([int(x) for x in dm.keys()])
    for key, values in dm.items():
        values = [(int(x[0]), int(x[1])) for x in values if int(x[1]) > 0]
        values = sorted(values, key=lambda x: x[0])
        nodes = [x[0] for x in values]
        combs = [x[1] for x in values]
        sd = 30 + 40 * int(key) / mx_f
        plt.plot(nodes, combs, color=p.red(shade=sd),
                 label=key, marker="o", ls="--")
        plt.annotate(f"{combs[-1]}", xy=(nodes[-1] + 0.1, combs[-1]),
                     va="center")
    plt.yscale("log")
    plt.title("type : 1, gates: 1, connected", pad=20)
    plt.xlabel("no. of nodes")
    plt.ylabel("no. of combinations")
    plt.legend(loc=0, ncol=2, title="Interactions")
    plt.gca().set_facecolor(p.gray(shade=15))
    plt.grid(axis="x", ls=":", color=p.gray(shade=40))
    plt.xlim(1.5, mx_f + 2)
    plt.tight_layout()
    plt.savefig("plot.png", dpi=300)
    plt.show()


def permutations(n, r):
    try:
        return math.factorial(n) / math.factorial(n - r)
    except ValueError:
        return 0


def calculate_combinations(n, r,
                           with_negative=False,
                           with_gates=True):
    # Number of possible pairs
    # 1 interaction will need 2 choices hence r+1
    # additional n will be for self loops

    pairs = permutations(n, 2) + n

    # Add interactions
    # We now need combinations and not permutations
    interactions = permutations(pairs, r) / math.factorial(r)
    if with_negative:
        # Add negative interactions
        # Every interaction will have choice of becoming positive or negative
        interactions = interactions * pow(2, r)

    if with_gates:
        multi_comb = n * (permutations(n, r) / math.factorial(r))
        single_pairs = interactions - multi_comb
        interactions = (interactions - single_pairs) * pow(2, r)
        interactions += 2 * multi_comb

    return interactions


def run():
    # plot_combinations()
    # generate_combinations()
    plot_single_node(5)
