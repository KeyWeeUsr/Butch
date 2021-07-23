"""
Abstraction of looking at a string as if via a film strip.

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
    Look on the flat text buffer/string as if it's a movie film strip.

    Film strip with two neighboring film windows for quick look-ahead and
    look-before access.
    """

    _data: str
    _data_len: int
    _pos: int
    _last_pos: int

    # previous, current and next
    _pchar: str
    _char: str
    _nchar: str

    def __init__(self, data: str, start: int = 0):
        self._data = data
        data_len = len(data)
        self._data_len = data_len
        self._last_pos = data_len - 1
        self._pchar = ""
        self._char = ""
        self._nchar = ""
        self._pos = 0

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
        """
        Move the film window by <pos> increments.

        Args:
            pos (int): index for the center film window
        """
        str_data = self.data
        data_len = self._data_len

        if not data_len:
            return

        self._pchar = ""
        if 0 <= pos - 1 < data_len:
            self._pchar = str_data[pos - 1]

        self._char = ""
        if 0 <= pos < data_len:
            self._char = str_data[pos]

        self._nchar = ""
        if 0 <= pos + 1 < data_len:
            self._nchar = str_data[pos + 1]
