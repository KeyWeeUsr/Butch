"""
Module containing class(es) for passing immutable values between functions
for accessing and mainly modifying its content. (Pass by reference, kind-of).
"""


class Shared:
    "Container to encapsulate the commonly immutable values."
    _data = None

    def __init__(self, data=None):
        self._data = data

    def set(self, value):
        "Set the raw data to ``value``."
        self._data = value

    def clear(self):
        "Clear the raw data to ``None``."
        self._data = None

    @property
    def data(self):
        "Property: raw data."
        return self._data

    def __bool__(self):
        return bool(self._data)

    def __repr__(self):
        return f"Shared({self._data!r})"
