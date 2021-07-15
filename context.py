import sys
import logging
from os import getcwd, environ
from time import strftime
from random import randint

PROMPT_SYMBOL = "$"
PROMPT_AMP = "$A"
PROMPT_PIPE = "$B"
PROMPT_LPARENT = "$C"
PROMPT_DATE = "$D"
PROMPT_ESCAPE = "$E"
PROMPT_RPARENT = "$F"
PROMPT_GREATER = "$G"
PROMPT_BACKSPACE = "$H"
PROMPT_LESSER = "$L"
PROMPT_DRIVE = "$N"
PROMPT_DRIVE_PATH = "$P"
PROMPT_EQUAL = "$Q"
PROMPT_SPACE = "$S"
PROMPT_TIME = "$T"
PROMPT_SYSTEMVERSION = "$V"
PROMPT_CRLF = "$_"
PROMPT_DOLLAR = "$$"
PROMPT_PUSHD_STACK_PLUS = "$+"
PROMPT_DRIVE_NETWORK = "$M"


class Context:
    _cwd: str = None
    _variables: dict = None
    _error_level: int = 0
    _extensions_enabled: bool = True
    _delayed_expansion_enabled: bool = False
    _dynamic_variables: list = [
        "cd", "date", "time", "random", "errorlevel",
        "cmdextversion", "cmdcmdline"
    ]
    _history: list = None
    _history_enabled: bool = True
    _echo: bool = True
    _prompt: str = ""
    __logger = None

    def __init__(self, **kwargs):
        self._variables = self._get_default_variables()
        self._history = []
        self.__logger = self.get_logger()
        self._prompt = self._variables.get("prompt", "")
        self._cwd = getcwd()

        for key, val in kwargs.items():
            if key not in dir(Context):
                raise Exception(f"Bad key: '{key}' (ignored)")
            setattr(self, f"_{key}", val)

    def __repr__(self):
        keys = [
            "cwd", "variables", "error_level", "extensions_enabled",
            "dynamic_variables", "history", "echo", "prompt",
            "delayed_expansion_enabled", "history_enabled"
        ]
        return str({key: getattr(self, key) for key in keys})

    @property
    def log(self):
        return self.__logger

    @property
    def cwd(self):
        return self._cwd

    @property
    def error_level(self):
        return self._error_level

    @error_level.setter
    def error_level(self, value):
        self._error_level = value

    @property
    def extensions_enabled(self):
        return self._extensions_enabled

    @extensions_enabled.setter
    def extensions_enabled(self, value):
        self._extensions_enabled = value

    @property
    def history_enabled(self):
        return self._history_enabled

    @history_enabled.setter
    def history_enabled(self, value):
        self._history_enabled = value

    @property
    def delayed_expansion_enabled(self):
        return self._delayed_expansion_enabled

    @delayed_expansion_enabled.setter
    def delayed_expansion_enabled(self, value):
        self._delayed_expansion_enabled = value

    @property
    def dynamic_variables(self):
        return self._dynamic_variables

    @property
    def variables(self):
        return self._variables

    def get_variable(self, key, delayed=False):
        if self.extensions_enabled and key in self.dynamic_variables:
            return self._get_dynamic_variable(key)
        return self.variables.get(key, f"%{key}%")

    def set_variable(self, key, value):
        self._variables[key] = value

    def delete_variable(self, key, value):
        del self._variables[key]

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, value):
        if not self.history_enabled:
            return
        self._history.append(value)

    @property
    def echo(self) -> bool:
        return self._echo

    @echo.setter
    def echo(self, value: bool):
        self._echo = value

    @property
    def prompt(self) -> bool:
        return self._prompt

    @prompt.setter
    def prompt(self, value: str):
        self._prompt = value
        self.set_variable("prompt", value)

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
            "prompt": f"{PROMPT_DRIVE_PATH}{PROMPT_GREATER}",
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

    def _get_dynamic_variable(self, name: str):
        if name == "cd":
            return getcwd()
        elif name == "date":
            return strftime("%x")
        elif name == "time":
            return strftime("%X")
        elif name == "random":
            return str(randint(0, 32767))
        elif name == "errorlevel":
            return str(self.error_level)
        elif name == "cmdextversion":
            return "2"
        elif name == "cmdcmdline":
            # TODO: point to main.py, check after pyinstaller
            return sys.executable
        return None

    def resolve_prompt(self) -> str:
        prompt = self.prompt
        if PROMPT_SYMBOL not in prompt:
            return prompt
        _, *flags = prompt.split(PROMPT_SYMBOL)
        flags = [f"${flag}" for flag in flags]

        out = ""
        for flag in flags:
            if flag == PROMPT_LESSER:
                out += "<"
                continue

            if flag == PROMPT_GREATER:
                out += ">"
                continue

            if flag == PROMPT_DRIVE_PATH:
                out += self.cwd
                continue
        return out

    @staticmethod
    def get_logger():
        logger = logging.getLogger(__name__)
        level = logging.INFO
        if environ.get("DEBUG"):
            level = logging.DEBUG
        logging.basicConfig(level=level, force=True)
        return logger


def get_context() -> dict:
    cwd = getcwd().replace("/", "\\")
    return Context(cwd=cwd)
