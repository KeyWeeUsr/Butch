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

    @property
    def pos(self):
        return self._pos

    @property
    def last_pos(self):
        return self._last_pos

    @property
    def data(self):
        return self._data

    def __len__(self):
        return self._data_len

    @property
    def pchar(self):
        return self._pchar

    @property
    def char(self):
        return self._char

    @property
    def nchar(self):
        return self._nchar

    def move(self, pos: int):
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
