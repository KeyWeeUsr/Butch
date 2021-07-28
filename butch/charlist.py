"""
Mix between a string and an array to behave like a buffer.

For passing between functions as a mutable parameter without guessing
the buffer.seek(N) number or even tracking it out of the container.
"""


class CharList:
    """
    Make a string mutable.

    Used to pass strings between functions to prevent repetition.
    """

    _data: str  # noqa: WPS110

    def __init__(self, data: str = ""):  # noqa: WPS110
        """
        Initialize CharList instance.

        Args:
            data (str): string to store
        """
        self._data = data  # noqa: WPS110

    def __iadd__(self, other: str):
        """
        Implement += operator.

        Args:
            other (str): string to append

        Returns:
            this instance
        """
        self._data += other  # noqa: WPS110
        return self

    @property
    def data(self):  # noqa: WPS110
        """
        Return the raw stored data.

        Returns:
            stored string
        """
        return self._data

    @data.setter
    def data(self, value: str):  # noqa: WPS110
        self._data = value  # noqa: WPS110

    def __repr__(self):
        """
        Get a string representation of the instance.

        Returns:
            string representation
        """
        return f"CharList({self._data!r})"

    def __bool__(self):
        """
        Booleanize the stored data.

        Returns:
            boolean
        """
        return bool(self._data)

    def clear(self):
        """Empty the buffer."""
        self._data = ""  # noqa: WPS110
