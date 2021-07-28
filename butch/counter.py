"""
Mutable itertools.counter().

Mitigates having immutable integer in one func and the whole copy-passing
stuff just to bump the value as well as builds on the usability of counter()
from itertools, but preserves the current value.
"""


class Count:  # noqa: WPS214
    """Like itertools.counter(), but is observable and a bit heavier."""

    _value: int  # noqa: WPS110
    _step: int
    _writable: bool

    def __init__(self, start: int = 0, step: int = 1, writable: bool = False):
        """
        Initialize Count instance.

        Args:
            start (int): start number
            step (int): increment
            writable (bool): can set value after initialization
        """
        self._value = start  # noqa: WPS110
        self._step = step
        self._writable = writable

    @property
    def value(self):  # noqa: WPS110
        """
        Get current value.

        Returns:
            current state
        """
        return self._value

    @value.setter
    def value(self, value: int):  # noqa: WPS110
        if not self._writable:
            raise AttributeError("can't set attribute")
        self._value = value  # noqa: WPS110

    @property
    def step(self):
        """
        Get step value.

        Returns:
            step number
        """
        return self._step

    @step.setter
    def step(self, value: int):  # noqa: WPS110
        if not self._writable:
            raise AttributeError("can't set attribute")
        self._step = value  # noqa: WPS110

    def __next__(self):
        """
        Go forward by step value.

        Returns:
            (int) next iteration
        """
        self._value += self._step  # noqa: WPS110
        return self._value

    def __reversed__(self):
        """
        Get back by step value.

        Returns:
            (int) previous iteration
        """
        self._value -= self._step  # noqa: WPS110
        return self._value

    def next(self):
        """
        Move forward by one step.

        Returns:
            (int) next iteration
        """
        return self.__next__()

    def previous(self):
        """
        Return back by one step.

        Returns:
            (int) previous iteration
        """
        return self.__reversed__()

    def __repr__(self):
        """
        Get a string representation of the instance.

        Returns:
            string representation
        """
        return f"count({self.value})"

    def __lt__(self, other: int):
        """
        Implement < operator.

        Args:
            other (int): int to compare with

        Returns:
            boolean
        """
        return self._value < other

    def __lte__(self, other: int):
        """
        Implement <= operator.

        Args:
            other (int): int to compare with

        Returns:
            boolean
        """
        return self._value <= other

    def __gt__(self, other: int):
        """
        Implement > operator.

        Args:
            other (int): int to compare with

        Returns:
            boolean
        """
        return self._value > other

    def __gte__(self, other: int):
        """
        Implement >= operator.

        Args:
            other (int): int to compare with

        Returns:
            boolean
        """
        return self._value >= other

    def __eq__(self, other: int):
        """
        Implement == operator.

        Args:
            other (int): int to compare with

        Returns:
            boolean
        """
        return self._value == other
