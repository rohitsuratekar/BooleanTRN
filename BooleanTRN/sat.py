#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#

from pprint import pprint

from z3 import Bools, Solver, Or, And, Not

x, y, z = Bools("x y z")
x1, y1, z1 = Bools("x1 y1 z1")


# x -> z
# y -| z
# !x -> !z

def add_positive_connection(solver: Solver, var1, var2):
    solver.add(Or(And(var1, var2), And(Not(var1), Not(var2))))


def add_negative_connection(solver: Solver, var1, var2):
    solver.add(Or(And(var1, Not(var2)), And(Not(var1), var2)))


def add_final_stat(solver: Solver, var, state):
    if state:
        solver.add(var)
    else:
        solver.add(Not(var))


def add_mutation_condition(solver: Solver, mutant, affected):
    pass


s = Solver()
add_positive_connection(s, x, z1)
add_negative_connection(s, y, z1)
add_final_stat(s, x1, True)
add_final_stat(s, z1, False)
add_final_stat(s, y1, True)
add_final_stat(s, x, True)
print(s.check())
pprint(s.model())
