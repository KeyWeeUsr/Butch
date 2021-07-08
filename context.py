import sys
from os import getcwd
from time import strftime
from random import randint


class Context:
    _cwd: str = None
    _variables: dict = None
    _error_level: int = 0
    _extensions_enabled: bool = False
    _dynamic_variables: list = [
        "cd", "date", "time", "random", "errorlevel",
        "cmdextversion", "cmdcmdline"
    ]

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
    def error_level(self):
        return self._error_level

    @error_level.setter
    def error_level(self, value):
        self._error_level = value

    def _get_dynamic_variable(name: str):
        if name == "cd":
            return getcwd()
        elif name == "date":
            return strftime("%x")
        elif name == "time":
            return strftime("%X")
        elif name == "random":
            return randint(0, 32767)
        elif name == "errorlevel":
            return self.error_level
        elif name == "cmdextversion":
            return 2
        elif name == "cmdcmdline":
            # TODO: point to main.py, check after pyinstaller
            return sys.executable
        return None

    @property
    def extensions_enabled(self):
        return self._extensions_enables

    @extensions_enabled.setter
    def extensions_enabled(self, value):
        self._extensions_enabled = value

    @property
    def dynamic_variables(self):
        return self._dynamic_variables

    @property
    def variables(self):
        return self._variables

    def get_variable(self, key):
        if self.extensions_enabled and key in self.dynamic_variables:
            return _get_dynamic_variable(key)
        self.variables.get(key, f"%{key}%")

    def set_variable(self, key, value):
        self._variables[key] = value

    def _get_default_variables(self):
        return {
            "allusersprofile": None,
            "appdata": None,
            "clientname": None,
            "commonprogramfiles": None,
            "computername": None,
            "comspec": None,
            "devmgr_show_nonpresent_devices": None,
            "fp_no_host_check": None,
            "homedrive": None,
            "homepath": None,
            "logonserver": None,
            "number_of_processors": None,
            "os": None,
            "path": None,
            "pathext": None,
            "processor_architecture": None,
            "processor_identifier": None,
            "processor_level": None,
            "processor_revision": None,
            "programfiles": None,
            "prompt": None,
            "sessionname": None,
            "systemdrive": None,
            "systemroot": None,
            "temp": None,
            "tmp": None,
            "userdomain": None,
            "username": None,
            "userprofile": None,
            "windir": None
        }


def get_context() -> dict:
    cwd = getcwd().replace("/", "\\")
    return Context(cwd=cwd)
