#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
# All analysis will be done here.

from typing import List

from BooleanTRN.models.basic import *
from BooleanTRN.models.basic import LogicalOperation as LogOp


def remove_redundant(operators: List[LogOp]) -> List[LogOp]:
    final_list = []
    dnf_list = []
    for op in operators:
        if op.short_dnf() not in dnf_list:
            final_list.append(op)
            dnf_list.append(op.short_dnf())
    return final_list


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

    return remove_redundant(final_list)


def unique_connections(variables: List[Union[LogOp, Variable]], target: bool):
    v = [[x, NOT(x)] for x in variables]
    temp_list = []
    for m in itertools.product(*v):
        temp_list.extend(assign_operators(list(m), target))

    final_list = []
    dnf_list = []
    for f in temp_list:
        if f.short_dnf() not in dnf_list:
            final_list.append(f)
            dnf_list.append(f.short_dnf())

    return final_list


def run():
    a = Variable("a", True)
    b = Variable("b", True)
    c = Variable("c", True)
    d = Variable("d", False)
    e = Variable("e", False)
    connections = unique_connections([a, b, c], False)
    print(len(connections))
