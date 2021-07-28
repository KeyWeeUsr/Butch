"""Module for input containers."""
from io import StringIO


class CommandInput:
    """Container for STDIN for redirection."""

    _stdin: StringIO

    def __init__(self, stdin: bool = True):
        """
        Initialize STDIN buffer based on params.

        Args:
            stdin (bool): should create STDIN buffer
        """
        # ask to allocate, don't provide custom though
        self._stdin = StringIO() if stdin else None

    @property
    def stdin(self):
        """
        Get the standard input buffer.

        Returns:
            StringIO buffer.
        """
        return self._stdin
