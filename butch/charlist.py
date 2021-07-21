"""
Mix between a string and an array to behave like a buffer, but without
guessing the buffer.seek(N) number or tracking it, so it can be passed
between functions as a mutable parameter.
"""


class CharList:
    """
    Because immutable strings when passed between functions don't help much
    for the tokenizer module.
    """

    _data: str = ""

    def __init__(self, data: str = ""):
        self._data = data

    def __iadd__(self, other: str):
        self._data += other
        return self

    @property
    def data(self):
        "Return the raw stored data."
        return self._data

    @data.setter
    def data(self, value: str):
        self._data = value

    def __repr__(self):
        return f"CharList({self._data!r})"

    def __bool__(self):
        return bool(self._data)

    def clear(self):
        "Empty the buffer."
        self._data = ""
