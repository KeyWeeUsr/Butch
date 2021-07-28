"""Module for output containers if simple print() or return isn't enough."""
from io import StringIO


class CommandOutput:
    """Container for STDOUT and STDERR buffers for piping and redirection."""

    _stdout: StringIO
    _stderr: StringIO

    def __init__(self, stdout: bool = True, stderr: bool = False):
        """
        Initialize STDOUT and/or STDERR buffers based on params.

        Args:
            stdout (bool): should create STDOUT buffer
            stderr (bool): should create STDERR buffer
        """
        # ask to allocate, don't provide custom though
        self._stdout = StringIO() if stdout else None
        self._stderr = StringIO() if stderr else None

    @property
    def stdout(self):
        """
        Get the standard output buffer.

        Returns:
            StringIO buffer.
        """
        return self._stdout

    @property
    def stderr(self):
        """
        Get the standard error buffer.

        Returns:
            StringIO buffer.
        """
        return self._stderr
