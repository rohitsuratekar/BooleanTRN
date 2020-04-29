#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
# Main file which will deal with all functions available in this library.

from BooleanTRN.models.basic import *

data = [
    ["a", "b", 1],
    ["b", "a", 1],
    ["c", "c", 0],
    ["d", "a", 1],
]

# Mutant, Affects, Positive/Negative
expectation = [
    ["a", "b", 1],
    ["a", "c", 1]
]

g = Graph()
g.make_from_data(data)
g.set_initial_condition({"a": False}, fill_default=True)
g.check_expectation(expectation)
