#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
#  All basic models


class Operations:

    def __int__(self):
        raise NotImplementedError

    def __eq__(self, other):
        return self.__int__() == other

    def __ne__(self, other):
        return self.__int__() != other

    def __lt__(self, other):
        return self.__int__() < other

    def __gt__(self, other):
        return self.__int__() > other

    def __le__(self, other):
        return self.__int__() <= other

    def __ge__(self, other):
        return self.__int__() >= other


class Variable(Operations):
    def __init__(self, name, state: bool):
        super().__init__()
        self.name = name
        self._current_state = state

    @property
    def state(self):
        return self._current_state

    @state.setter
    def state(self, value: bool):
        self._current_state = value

    def __bool__(self):
        return self.state

    def __repr__(self):
        return f"Variable({self.name})"

    def __str__(self):
        return self.name

    def __int__(self):
        return int(self.state)


class LogicalOperation(Operations):
    def __init__(self, *args):
        self.args = args

    @property
    def type(self) -> str:
        raise NotImplementedError

    def state(self) -> bool:
        raise NotImplementedError

    def __bool__(self):
        return self.state()

    def __int__(self):
        return int(self.__bool__())

    def __str__(self):
        return self.formatted()

    def __repr__(self):
        return f"LogicalOperation({self.__bool__()})"

    def formatted(self) -> str:
        current = "("

        if self.__class__ == NOT:
            current += f" NOT {str(self.args[0])} )"
            return current

        for a in self.args:
            current += f" {str(a)} "
            if id(a) != id(self.args[-1]):
                current += self.type
        current += ")"
        return current


class OR(LogicalOperation):

    @property
    def type(self) -> str:
        return "OR"

    def state(self) -> bool:
        return bool(max(self.args))


class AND(LogicalOperation):

    @property
    def type(self) -> str:
        return "AND"

    def state(self) -> bool:
        return bool(min(self.args))


class NOT(LogicalOperation):

    def __init__(self, *args):
        super().__init__(*args)
        if len(args) != 1:
            raise ValueError(
                "NOT operation should have exactly one logical variable")

    @property
    def type(self) -> str:
        return "NOT"

    def state(self) -> bool:
        return not bool(self.args[0])


def run():
    a = Variable("a", True)
    b = Variable("b", True)
    c = Variable("c", True)

    f = AND(AND(a, b), c)
    print(f)
