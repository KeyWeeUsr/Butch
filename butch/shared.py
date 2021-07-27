"""
Module containing class(es) for passing immutable values between functions.

Used mainly for accessing and modifying its content.
(Pass by reference, kind-of).
"""

from typing import Any


class Shared:
    """Container to encapsulate the commonly immutable values."""

    _data: Any  # noqa: WPS110

    def __init__(self, data=None):  # noqa: WPS110
        """Initialize the mutable storage.

        Args:
            data: can be any Python object
        """
        self._data = data  # noqa: WPS110

    def set(self, value):  # noqa: WPS110
        """
        Set the stored data to ``value``.

        Args:
            value (object): anything to store.
        """
        self._data = value  # noqa: WPS110

    def clear(self):
        """Clear the stored data to ``None``."""
        self._data = None  # noqa: WPS110

    @property
    def data(self):  # noqa: WPS110
        """
        Getter for the stored data.

        Returns:
            anything that has been added to the object via __init__() or set().
        """
        return self._data

    def __bool__(self):
        """
        Evaluate the stored data as a boolean.

        Returns:
            bool(<stored data>)
        """
        return bool(self._data)

    def __repr__(self):
        """
        Return string representation of the object.

        Returns:
            stringified raw data encapsulated in the class representation
        """
        return f"Shared({self._data!r})"
