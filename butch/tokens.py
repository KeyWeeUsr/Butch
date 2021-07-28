"""Module for storing the tokens for tokenizer."""


class Argument:
    """Token holding the raw value of an argument and its properties."""

    _value: str  # noqa: WPS110
    _quoted: bool

    def __init__(self, value: str, quoted: bool = False):  # noqa: WPS110
        """
        Initialize Argument instance.

        Args:
            value (str): raw argument value to store
            quoted (bool): flag if the value is encapsulated in quotes
        """
        self._value = value  # noqa: WPS110
        self._quoted = quoted

    @property
    def value(self):  # noqa: WPS110
        """
        Raw raw argument value.

        Returns:
            whatever was stored
        """
        return self._value

    @value.setter
    def value(self, value):  # noqa: WPS110
        self._value = value  # noqa: WPS110

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

    def __eq__(self, other):
        """
        Check if two Argument instances have the same content.

        Args:
            other (Any): value to compare current instance with

        Returns:
            boolean for content equality
        """
        if not isinstance(other, Argument):
            return False
        return self.value == other.value
