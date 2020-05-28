#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
# All analysis will be done here.

import itertools
from typing import List, Union

from BooleanTRN.models.basic import *
from BooleanTRN.models.basic import LogicalOperation as LogOp


def remove_redundant(operators: List[LogOp]):
    for op in operators:
        print(op)


def assign_operators(variables: List[Union[LogOp, Variable]], target: bool):
    ops = [AND, OR]
    final_list = []
    for vm in itertools.permutations(variables, len(variables)):
        for m in itertools.product(ops, repeat=len(variables) - 1):
            cond = None
            for i, k in enumerate(m):
                if cond is None:
                    cond = k(vm[i], vm[i + 1])
                else:
                    cond = k(cond, vm[i + 1])

            if bool(cond) == target:
                final_list.append(cond)
    remove_redundant(final_list)


def test(variables: List[Union[LogOp, Variable]], target: bool):
    v = [[x, NOT(x)] for x in variables]
    final_list = []
    for m in itertools.product(*v):
        assign_operators(list(m), target)
        break


def run():
    a = Variable("a", True)
    b = Variable("b", True)
    c = Variable("c", False)
    d = Variable("d", False)
    test([a, b, c], True)
