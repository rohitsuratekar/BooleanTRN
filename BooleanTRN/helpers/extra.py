#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
# Extra functions which are not directly related to the analysis but helped
# in representing data.

from BooleanTRN.constants import BASE_NODES
from SecretPlots import BooleanPlot
from collections import defaultdict
from SecretColors import Palette


def plot_expression_state_matrix(data: list):
    """
    Data should be in following form
    (gene(str), expression_stat(bool), time(int))

    :param data: Data to be plotted
    """
    p = Palette()
    tps = []
    nodes_dict = defaultdict(dict)
    for d in data:
        nodes_dict[d[0]][d[2]] = d[1]
        tps.append(d[2])
    tps = list(set(tps))
    nodes = list(nodes_dict.keys())
    nor_data = []
    for n in nodes:
        tmp = []
        for time in tps:
            tmp.append(int(nodes_dict[n][time]))
        nor_data.append(tmp)

    bp = BooleanPlot(nor_data, 1)
    bp.add_x_midlines(color=p.white())
    bp.add_y_midlines(color=p.white())
    bp.add_x_top_ticks()
    bp.change_orientation("y")
    bp.y_ticklabels = nodes
    bp.add_x_padding(0, 0)
    bp.add_y_padding(0, 0)
    bp.change_aspect_ratio(1)
    bp.remove_frame()
    bp.remove_cmap()
    bp.x_ticklabels = [f"{t} hrs" for t in tps]
    bp.add_on_color(p.green(shade=30))
    bp.draw()
    bp.ax.get_legend().remove()
    bp.save("plot.png", dpi=300, transparent=True)
    bp.show()


def run():
    data = [(x, True, 24) for x in BASE_NODES]
    data2 = [(x, True, 72) for x in BASE_NODES]
    data.extend(data2)
    plot_expression_state_matrix(data)
