#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
#  All basic oldmodels

import itertools
from typing import Union


def convert_to_short_hand(opt_list, connector: str):
    def _attach(v: Union[Variable, NOT]) -> str:
        if isinstance(v, Variable):
            return f"{v.name}"
        elif isinstance(v, NOT):
            return f"{v.args[0].name}_not"
        else:
            return f"{v.short()}"

    main_list = []

    for op in opt_list:

        if isinstance(op, OR) or isinstance(op, AND):
            temp_str = []
            tmp_connect = op.type
            for a in op.args:
                temp_str.append(_attach(a))
            temp_str = sorted(temp_str)
            main_list.append(f"_{tmp_connect}_".join(temp_str))
        else:
            main_list.append(_attach(op))

    main_list = sorted(main_list)

    return f"_{connector}_".join(main_list)


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
        self.name = name  # type:str
        self._current_state = state  # type:bool

    @property
    def state(self):
        return self._current_state

    @state.setter
    def state(self, value: bool):
        self._current_state = value

    @property
    def sort_key(self):
        return self.name.strip()

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
        self._variables = None

    @property
    def type(self) -> str:
        raise NotImplementedError

    def state(self) -> bool:
        raise NotImplementedError

    @property
    def variables(self) -> list:
        if self._variables is None:
            all_vars = []

            def _add(v: Variable):
                if v.name not in [x.name for x in all_vars]:
                    all_vars.append(v)

            for a in self.args:
                if isinstance(a, Variable):
                    _add(a)
                elif isinstance(a, LogicalOperation):
                    for m in a.variables:
                        _add(m)

            self._variables = all_vars
        return self._variables

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
        if not ("AND" in current or "OR" in current):
            current = current.lstrip("(").rstrip(")").strip()
        return current

    def get_truth_table(self) -> list:
        original = {x.name: x.state for x in self.variables}
        var_dict = {x.name: x for x in self.variables}
        opts = [[True, False] for x in self.variables]
        names = [x.name for x in self.variables]
        tt = sorted([x for x in names])
        tt = [[tuple(tt), "f(x)"]]
        for k in itertools.product(*opts):
            temp = []
            for name, value in zip(names, k):
                var_dict[name].state = value
            temp.append(k)
            temp.append(self.state())
            tt.append(temp)
        # Remover truth value to the original
        for k, v in original.items():
            var_dict[k].state = v
        return tt

    def print_tt(self):
        for x in self.get_truth_table():
            print(f"{x[0]} \t {x[1]}")

    def cnf_literals(self):
        all_vars = {x.name: x for x in self.variables}
        tt = self.get_truth_table()
        all_index = [x for x in range(len(tt)) if tt[x][1] is False]
        cnf_fuc = []
        for i in all_index:
            tmp = []
            for x in tt[0][0]:
                ind = list(tt[0][0]).index(x)
                if tt[i][0][ind]:
                    tmp.append(NOT(all_vars[x]))
                else:
                    tmp.append(all_vars[x])
            tmp = sorted(tmp, key=lambda x: x.sort_key)
            cnf_fuc.append(OR(*tmp))
        return cnf_fuc

    def cnf(self):
        cnf_fuc = self.cnf_literals()
        if len(cnf_fuc) == 0:
            return self
        elif len(cnf_fuc) == 1:
            return cnf_fuc[0]
        return AND(*cnf_fuc)

    def dnf_literals(self) -> list:
        all_vars = {x.name: x for x in self.variables}
        tt = self.get_truth_table()
        all_index = [x for x in range(len(tt)) if tt[x][1] is True]
        dnf_fuc = []
        for i in all_index:
            tmp = []
            for x in tt[0][0]:
                ind = list(tt[0][0]).index(x)
                if tt[i][0][ind]:
                    tmp.append(all_vars[x])
                else:
                    tmp.append(NOT(all_vars[x]))
            tmp = sorted(tmp, key=lambda x: x.sort_key)
            dnf_fuc.append(AND(*tmp))
        return dnf_fuc

    def dnf(self):
        dnf_fuc = self.dnf_literals()
        if len(dnf_fuc) == 0:
            return self
        elif len(dnf_fuc) == 1:
            return dnf_fuc[0]
        return OR(*dnf_fuc)

    def short_dnf(self):
        return convert_to_short_hand(self.dnf_literals(), "OR")

    def short_cnf(self):
        return convert_to_short_hand(self.cnf_literals(), "AND")

    def short(self):
        return convert_to_short_hand(self.args, self.type)


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

    @property
    def sort_key(self):
        return f"{self.args[0].sort_key}_not"
