class Shared:
    _data = None

    def __init__(self, data=None):
        self._data

    def set(self, value):
        self._data = value

    def clear(self):
        self._data = None

    @property
    def data(self):
        return self._data

    def __bool__(self):
        return bool(self._data)

    def __repr__(self):
        return f"Shared({self._data!r})"
