from io import BytesIO


class CommandOutput:
    _stdout: BytesIO = None
    _stderr: BytesIO = None

    def __init__(self, stdout: bool = True, stderr: bool = False):
        # ask to allocate, don't provide custom though
        self._stdout = BytesIO()
        self._stderr = BytesIO()

    @property
    def stdout(self):
        return self._stdout

    @property
    def stderr(self):
        return self._stderr
