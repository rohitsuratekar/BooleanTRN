#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
# Bottom up approach

from collections import defaultdict
from BooleanTRN.models.logic import *
from BooleanTRN.models.network import Network
from BooleanTRN.models.graphics import draw_state_space
from BooleanTRN.constants import BASE_NETWORK


def cardio_network():
    nkx25 = Variable("nkx2.5", True)
    gata4 = Variable("gata4", True)
    tbx5a = Variable("tbx5a", True)
    mef2c = Variable("mef2c", True)
    hand2 = Variable("hand2", True)

    data = {
        nkx25.name: OR(gata4, tbx5a),
        gata4.name: tbx5a,
        tbx5a.name: nkx25,
        mef2c.name: OR(nkx25, gata4, tbx5a),
        hand2.name: OR(gata4, mef2c)
    }

    n = Network(data)
    draw_state_space(n)


def auto_net():
    all_nodes = {}
    for b in BASE_NETWORK:
        if b[0] not in all_nodes:
            all_nodes[b[0]] = Variable(b[0], True)
        for k in b[1]:
            if k not in all_nodes:
                all_nodes[k] = Variable(k, True)

    data = {}


def run():
    auto_net()
    # cardio_network()
    # a = Variable("a", True)
    # b = Variable("b", True)
    # # c = Variable("c", True)
    # #
    # data = {"a": AND(a, b)}
    # n = Network(data)
    # # n.print_states()
    # draw_state_space(n)
