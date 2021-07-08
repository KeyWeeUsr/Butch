from os import getcwd


class Context:
    _cwd: str = None

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key not in dir(Context):
                raise Exception(f"Bad key: '{key}' (ignored)")
            setattr(self, f"_{key}", val)

    @property
    def cwd(self):
        return self._cwd

def get_context() -> dict:
    cwd = getcwd().replace("/", "\\")
    return Context(cwd=cwd)
