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
        return self._data

    @data.setter
    def data(self, value: str):
        self._data = value

    def __repr__(self):
        return f"CharList({self._data!r})"

    def __bool__(self):
        return bool(self._data)

    def clear(self):
        self._data = ""
