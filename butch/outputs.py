"Module for output containers if simple print() or return isn't enough."
from io import StringIO


class CommandOutput:
    "Container for STDOUT and STDERR buffers for piping and redirection."

    _stdout: StringIO = None
    _stderr: StringIO = None

    def __init__(self, stdout: bool = True, stderr: bool = False):
        # ask to allocate, don't provide custom though
        if stdout:
            self._stdout = StringIO()
        if stderr:
            self._stderr = StringIO()

    @property
    def stdout(self):
        "Property: standard output buffer."
        return self._stdout

    @property
    def stderr(self):
        "Property: standard error buffer."
        return self._stderr
