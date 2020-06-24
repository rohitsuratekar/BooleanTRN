#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
# All logical models can go here

class Operations:
    """
    Common class to add mathematical operation functions.

    Note: __eq__ and __nq__ is not implemented because we want functionality
    to compare these classed by ID. Specifically when we need to check if
    specific class is present in given list or not.
    """

    def __int__(self):
        raise NotImplementedError

    def __lt__(self, other):
        return self.__int__() < other

    def __gt__(self, other):
        return self.__int__() > other

    def __le__(self, other):
        return self.__int__() <= other

    def __ge__(self, other):
        return self.__int__() >= other


class Variable(Operations):
    def __init__(self,
                 name: str,
                 initial_state: bool,
                 record_history: bool = False):
        self.name = name.strip()
        self._initial_state = initial_state
        self._current_state = initial_state
        self.record_history = record_history
        self._history = [initial_state]

    @property
    def state(self):
        return self._current_state

    @property
    def history(self) -> list:
        return self._history

    def _update_history(self):
        if self.record_history:
            self._history.append(self._current_state)

    @state.setter
    def state(self, value: bool):
        self._current_state = value
        self._update_history()

    def reset_history(self):
        self._history = [self._initial_state]

    def reset(self):
        self._current_state = self._initial_state

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var({self.name})"

    def __bool__(self):
        return self.state

    def __int__(self):
        return int(self.__bool__())


class LogOp(Operations):
    def __init__(self, *args):
        self.args = args

    @property
    def state(self) -> bool:
        raise NotImplementedError

    @property
    def type(self):
        raise NotImplementedError

    def get_variables(self) -> list:
        all_vars = []
        for a in self.args:
            if isinstance(a, Variable) and a not in all_vars:
                all_vars.append(a)
            elif isinstance(a, LogOp):
                for tmp in a.get_variables():
                    if tmp not in all_vars:
                        all_vars.append(tmp)
        return all_vars

    def __bool__(self):
        return self.state

    def __int__(self):
        return int(self.__bool__())

    def __str__(self):
        return f"{self.type}({' , '.join([str(x) for x in self.args])})"


class AND(LogOp):

    @property
    def type(self):
        return "AND"

    @property
    def state(self) -> bool:
        return min(self.args).__bool__()


class OR(LogOp):

    @property
    def type(self):
        return "OR"

    @property
    def state(self) -> bool:
        return max(self.args).__bool__()


class NOT(LogOp):

    def __init__(self, *args):
        super().__init__(*args)
        if len(self.args) != 1:
            raise ValueError(f"NOT should have only one variable. currently "
                             f"given {len(self.args)}")

    @property
    def type(self):
        return "NOT"

    @property
    def state(self) -> bool:
        return not self.args[0].__bool__()


def run():
    a = Variable("a", True)
    b = Variable("b", False)

    print(OR(a, False).state)
