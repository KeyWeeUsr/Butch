"""
Abstraction of looking at a string as if via a film strip:

                                 film window
                +--------------+--------------+--------------+
================|==============|==============|==============|=================
                |              |              |              |
                |   previous   |    current   |     next     |
                |              |              |              |
================|==============|==============|==============|=================
                +--------------+--------------+--------------+
"""


class FilmBuffer:
    """
    Look on the flat text buffer/string as if it's a movie film strip with
    two neighboring film windows.
    """

    _data: str = ""
    _data_len: int = 0
    _pos: int = 0
    _last_pos: int = 0

    # previous, current and next
    _pchar: str = ""
    _char: str = ""
    _nchar: str = ""

    def __init__(self, data: str, start: int = 0):
        self._data = data
        data_len = len(data)
        self._data_len = data_len
        self._last_pos = data_len - 1

        # initialize chars and positions by the first window move
        self.move(pos=start)

    @property
    def pos(self):
        "Property: current position of the film window."
        return self._pos

    @property
    def last_pos(self):
        "Property: last position of the buffer (len(data) - 1)."
        return self._last_pos

    @property
    def data(self):
        "Property: raw data."
        return self._data

    def __len__(self):
        return self._data_len

    @property
    def pchar(self):
        "Property: previous character / neighboring character to the left."
        return self._pchar

    @property
    def char(self):
        "Property: current character."
        return self._char

    @property
    def nchar(self):
        "Property: next character / neighboring character to the right."
        return self._nchar

    def move(self, pos: int):
        "Move the film window by <pos> increments."
        data = self.data
        data_len = self._data_len

        if not data_len:
            return

        self._pchar = ""
        if 0 <= pos - 1 < data_len:
            self._pchar = data[pos - 1]

        self._char = ""
        if 0 <= pos < data_len:
            self._char = data[pos]

        self._nchar = ""
        if 0 <= pos + 1 < data_len:
            self._nchar = data[pos + 1]
