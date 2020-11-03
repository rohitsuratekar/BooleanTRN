#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
#  All statistics visualizations

import csv
from collections import defaultdict
from multiprocessing import Process, Queue

import matplotlib
import matplotlib.pylab as plt
from SecretColors import Palette

from BooleanTRN.models.sweeps import NetworkAnalyser

matplotlib.rc("font", family="IBM Plex Sans")


def cal_comb(q, network: NetworkAnalyser):
    c = 0
    for _ in network.find_networks():
        c += 1
    q.put((network.no_of_nodes, network.no_of_edges, c))


def generate_combinations():
    q = Queue()
    actions = 4
    all_process = []
    for j in range(1, actions):
        for i in range(2, 8):
            na = NetworkAnalyser(i, j, allow_negative=True)
            p = Process(target=cal_comb, args=(q, na))
            p.start()
            all_process.append(p)

    data = []
    for _ in all_process:
        data.append(q.get())
        print(data[-1])

    with open("out.csv", "w") as f:
        print("nodes,edges,combinations", file=f)
        for d in data:
            print(",".join([str(x) for x in d]), file=f)

    print("Finished")


def plot_combinations():
    p = Palette()
    dm = defaultdict(list)
    with open("data/single.csv") as f:
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
    plt.title("type : 1, gates: 1", pad=20)
    plt.xlabel("no. of nodes")
    plt.ylabel("no. of combinations")
    plt.legend(loc=0, ncol=2, title="Interactions")
    plt.gca().set_facecolor(p.gray(shade=15))
    plt.grid(axis="x", ls=":", color=p.gray(shade=40))
    plt.xlim(1.5, mx_f + 2)
    plt.tight_layout()
    plt.savefig("plot.png", dpi=300)
    plt.show()


def run():
    # plot_combinations()
    generate_combinations()