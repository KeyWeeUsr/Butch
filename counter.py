"""
Mitigates having immutable integer in one func and the whole copy-passing
stuff just to bump the value as well as builds on the usability of counter()
from itertools, but preserves the current value.
"""


class Count:
    "Like itertools.counter(), but this one is observable, but also heavier."

    _value: int = 0
    _step: int = 0
    _writable: bool = False

    def __init__(self, start: int = 0, step: int = 1, writable: bool = False):
        self._value = start
        self._step = step
        self._writable = writable

    @property
    def value(self):
        "Property: current value."
        return self._value

    @value.setter
    def value(self, value: int):
        if not self._writable:
            raise AttributeError("can't set attribute")
        self._value = value

    @property
    def step(self):
        "Property: step value."
        return self._step

    @step.setter
    def step(self, value: int):
        if not self._writable:
            raise AttributeError("can't set attribute")
        self._step = value

    def __next__(self):
        self._value += self._step
        return self._value

    def __reversed__(self):
        self._value -= self._step
        return self._value

    def next(self):
        "Move forward by one step."
        return self.__next__()

    def previous(self):
        "Return back by one step."
        return self.__reversed__()

    def __repr__(self):
        return f"count({self.value})"

    def __lt__(self, other: int):
        return self._value < other

    def __lte__(self, other: int):
        return self._value <= other

    def __gt__(self, other: int):
        return self._value > other

    def __gte__(self, other: int):
        return self._value >= other

    def __eq__(self, other: int):
        return self._value == other
