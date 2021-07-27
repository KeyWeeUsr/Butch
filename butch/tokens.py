"""Module for storing the tokens for tokenizer."""


class Argument:
    "Token holding the raw value of an argument and its properties."

    _value: str = ""
    _quoted: bool = False

    def __init__(self, value: str, quoted: bool = False):
        self._value = value
        self._quoted = quoted

    @property
    def value(self):
        "Property: raw argument value."
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def quoted(self):
        "Property: argument value is quoted."
        return self._quoted

    def __repr__(self):
        val = self._value
        if self.quoted:
            val = repr(val)
        return f"<Argument: {val!r}, q={int(self.quoted)}>"

    def __eq__(self, other):
        if not isinstance(other, Argument):
            return False
        return self.value == other.value
