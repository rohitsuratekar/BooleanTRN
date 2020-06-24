#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
# All analysis will be done here.

from typing import List

from BooleanTRN.oldmodels.basic import *
from BooleanTRN.oldmodels.basic import LogicalOperation as LogOp


class Condition:
    def __int__(self):
        pass


def remove_redundant(operators: List[LogOp]) -> List[LogOp]:
    extra_var = [x for x in operators if isinstance(x, Variable)]
    final_list = []
    dnf_list = []
    short_list = []
    for op in [x for x in operators if not isinstance(x, Variable)]:
        if (op.short_dnf() not in dnf_list) and (op.short() not in short_list):
            final_list.append(op)
            dnf_list.append(op.short_dnf())
            short_list.append(op.short())
    final_list.extend(extra_var)
    return final_list


def assign_operators(variables: List[Union[LogOp, Variable]], target: bool,
                     ops: List[LogOp]):
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


def unique_connections(variables: List[Variable],
                       target: bool,
                       ops: list):
    if len(variables) == 1:
        if target == variables[0].state:
            return [variables[0]]
        else:
            return [NOT(variables[0])]
    v = [[x, NOT(x)] for x in variables]
    temp_list = []
    for m in itertools.product(*v):
        temp_list.extend(assign_operators(list(m), target, ops))
    return remove_redundant(temp_list)


def variable_combinations(variables: List[Variable], target: bool):
    opts = [OR, AND]
    all_combinations = []
    for number in range(1, len(variables) + 1):
        for current in itertools.combinations(variables, number):
            connections = unique_connections(list(current), target, opts)
            all_combinations.extend(connections)

    all_combinations = remove_redundant(all_combinations)


def run():
    a = Variable("a", False)
    b = Variable("b", True)
    c = Variable("c", True)
    d = Variable("d", False)
    e = Variable("e", False)
    ops = [OR, AND]
    variable_combinations([a, b, c, d], True)
