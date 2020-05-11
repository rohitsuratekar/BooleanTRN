#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
# All network related models will go here

from BooleanTRN.models.basic import Variable


class Node:
    def __init__(self, name: str, state: bool = True):
        self.name = name
        self.state = state
        self._variable = None

    @property
    def variable(self):
        if self._variable is None:
            self._variable = Variable(self.name, self.state)
        return self._variable


def run():
    a = Node("a")
    b = Node("b")
