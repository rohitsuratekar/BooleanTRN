#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#

import matplotlib.pyplot as plt
from SecretColors import Palette
from collections import Counter
from matplotlib.patches import Patch


def plot_node_degrees(degree_direction: dict, xlabel: str):
    p = Palette()
    labels = [x for x in degree_direction.keys()]
    colors = [p.red(shade=40), p.blue(shade=30),
              p.blue(shade=40), p.blue(shade=50),
              p.blue(shade=60)]
    all_in_degrees = [y for x in degree_direction.values() for y in x]
    all_in_degrees = list(set(all_in_degrees))

    for idx, degree in enumerate(all_in_degrees):
        ctr = Counter()
        for d in degree_direction:
            for k in degree_direction[d]:
                if k == degree:
                    ctr.update({d})

        values = []
        for m in labels:
            if m in ctr:
                values.append(ctr[m])
            else:
                values.append(0)

        total = sum(values)
        values = [x * 100 / total for x in values]
        below = 0
        for m in range(len(values)):
            plt.bar(idx, values[m], bottom=below, color=colors[m])
            below += values[m]

    handles = []
    for i, p in enumerate(colors):
        if i == 0:
            i = "nkx2.5"
        handles.append(Patch(facecolor=p, label=f"{i}"))

    plt.legend(handles=handles, loc="lower center",
               ncol=5,
               bbox_to_anchor=(0, 1, 1, 0))
    plt.xticks(range(len(all_in_degrees)), all_in_degrees)
    plt.xlabel(xlabel)
    plt.ylabel("% of times appeared in networks")
    plt.tight_layout()
    plt.savefig("plot.png", dpi=300)
    plt.show()
