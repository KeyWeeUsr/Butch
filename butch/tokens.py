"""Module for storing the tokens for tokenizer."""

from typing import Any


class Token:
    pass


class BaseValue(Token):
    """Base for a token holding the raw value with repr() and == operator."""

    _value: str  # noqa: WPS110

    def __init__(self, value: str):  # noqa: WPS110
        """
        Initialize BaseValue instance.

        Args:
            value (str): raw value to store
        """
        self._value = value  # noqa: WPS110

    @property
    def value(self):  # noqa: WPS110
        """
        Raw value.

        Returns:
            whatever was stored
        """
        return self._value

    @value.setter
    def value(self, value):  # noqa: WPS110
        self._value = value  # noqa: WPS110

    def __repr__(self):
        """
        Get a string representation of this instance.

        Returns:
            string representation
        """
        return f"<{self.__class__.__name__}: {self._value!r}>"

    def __eq__(self, other):
        """
        Check if two instances have the same content.

        Args:
            other (Any): value to compare current instance with

        Returns:
            boolean for content equality
        """
        if not isinstance(other, BaseValue):
            return False
        return self.value == other.value


class Argument(BaseValue):
    """Token holding the raw value of an argument and its properties."""

    _quoted: bool

    def __init__(self, value: str, quoted: bool = False):  # noqa: WPS110
        """
        Initialize Argument instance.

        Args:
            value (str): raw argument value to store
            quoted (bool): flag if the value is encapsulated in quotes
        """
        super().__init__(value=value)
        self._quoted = quoted

    @property
    def quoted(self):
        """
        Get if the Argument is quoted.

        Returns:
            boolean
        """
        return self._quoted

    def __repr__(self):
        """
        Get a string representation of Argument instance.

        Returns:
            string representation
        """
        stored = self._value
        quoted = int(self.quoted)
        if quoted:
            stored = repr(stored)
        return f"<Argument: {stored!r}, q={quoted}>"


class File(BaseValue):
    "Token holding the raw value of filename for redirection."

    def __init__(self, value: str = ""):  # noqa: WPS110
        """
        Initialize File instance.

        Args:
            value (str): raw filename to store, defaults to empty string
        """
        super().__init__(value=value)


class Label(BaseValue):
    "Token holding the raw value of label for a GOTO command."


class Block(Token):
    """Block of commands to execute in specific order."""

    _values: list  # noqa: WPS110

    def __init__(self, values: list):  # noqa: WPS110
        """
        Initialize Block instance.

        Args:
            values (list): raw list of tokens to store
        """
        self._values = values  # noqa: WPS110

    @property
    def values(self):  # noqa: WPS110
        """
        Raw values.

        Returns:
            whatever was stored
        """
        return self._values

    @values.setter
    def values(self, values):  # noqa: WPS110
        self._values = values  # noqa: WPS110

    def __repr__(self):
        """
        Get a string representation of this instance.

        Returns:
            string representation
        """
        return f"<{self.__class__.__name__}: {self._values!r}>"

    def __len__(self):
        """
        Get a length of values in this instance.

        Returns:
            int
        """
        return len(self.values)

    def __iter__(self):
        return self.values.__iter__()

    def __eq__(self, other: Any):
        if not isinstance(other, Block):
            return False

        own_vals = self.values
        other_vals = other.values
        if len(own_vals) != len(other_vals):
            return False

        for left, right in zip(own_vals, other_vals):
            if left != right:
                return False
        return True
