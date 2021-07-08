from os import getcwd


class Context:
    _cwd: str = None
    _variables: dict = None

    def __init__(self, **kwargs):
        self._variables = {}

        for key, val in kwargs.items():
            if key not in dir(Context):
                raise Exception(f"Bad key: '{key}' (ignored)")
            setattr(self, f"_{key}", val)

    @property
    def cwd(self):
        return self._cwd

    @property
    def variables(self):
        return self._variables

    def set_variable(self, key, value):
        self._variables[key] = value


def get_context() -> dict:
    cwd = getcwd().replace("/", "\\")
    return Context(cwd=cwd)
