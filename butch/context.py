"""Module for global or local (command) state related classes and functions."""

import sys
from os import getcwd
from time import strftime
from random import randint

from butch.outputs import CommandOutput
from butch.logger import get_logger

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
DYNAMIC_RAND_MAX = 32767


class Context:
    """
    Holds the state in-between the commands and the overall, global state
    of the Batch language interpreter.
    """
    # pylint: disable=too-many-instance-attributes

    _cwd: str = None
    _variables: dict = None
    _error_level: int = 0
    _extensions_enabled: bool = True
    _delayed_expansion_enabled: bool
    _dynamic_variables: list = [
        "cd", "date", "time", "random", "errorlevel",
        "cmdextversion", "cmdcmdline"
    ]
    _history: list = None
    _history_enabled: bool
    _echo: bool
    _prompt: str
    _output: CommandOutput = None
    _collect_output: bool = False
    _piped: bool = False
    __logger = None

    def __init__(self, **kwargs):
        self._variables = self._get_default_variables()
        self._history = []
        self.__logger = get_logger()
        self._prompt = self._variables.get("prompt", "")
        self._cwd = getcwd()
        self._echo = True
        self._delayed_expansion_enabled = False
        self._history_enabled = True

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
        """
        Property.

        Returns:
            reference to the Butch's logger.
        """
        return self.__logger

    @property
    def cwd(self):
        """
        Property.

        Returns:
            current working directory.
        """
        return self._cwd

    @property
    def error_level(self):
        """
        Property.

        Returns:
            current error level of a script.
        """
        return self._error_level

    @error_level.setter
    def error_level(self, value):
        self._error_level = value

    @property
    def piped(self):
        """
        Property.

        Returns:
            flag whether the previous command was piped.
        """
        return self._piped

    @piped.setter
    def piped(self, value):
        self._piped = value

    @property
    def collect_output(self):
        """
        Property.

        Returns:
            flag whether to collect output to pipe or redirection.
        """
        return self._collect_output

    @collect_output.setter
    def collect_output(self, value):
        self._collect_output = value

    @property
    def output(self):
        """
        Property.

        Returns:
            stored output / passed input if piped or redirected.
        """
        return self._output

    @output.setter
    def output(self, value):
        self._output = value

    @property
    def extensions_enabled(self):
        """
        Property.

        Returns:
            Batch extensions flag.
        """
        return self._extensions_enabled

    @extensions_enabled.setter
    def extensions_enabled(self, value):
        self._extensions_enabled = value

    @property
    def history_enabled(self):
        """
        Property.

        Returns:
            flag if executed commands should be collected.
        """
        return self._history_enabled

    @history_enabled.setter
    def history_enabled(self, enabled):
        self._history_enabled = enabled

    @property
    def delayed_expansion_enabled(self):
        """
        Property.

        Returns:
            flag whether to expand variables with ! (exc.mark).
        """
        return self._delayed_expansion_enabled

    @delayed_expansion_enabled.setter
    def delayed_expansion_enabled(self, enabled):
        self._delayed_expansion_enabled = enabled

    @property
    def dynamic_variables(self):
        """
        Property.

        Returns:
            list of dynamic variables' names.
        """
        return self._dynamic_variables

    @property
    def variables(self):
        """
        Property.

        Returns:
            all stored variables in the context except dynamic
        """
        return self._variables

    # pylint: disable=unused-argument
    def get_variable(self, key, delayed=False):
        """
        Get a value of variable from the context.

        Args:
            key: variable name
            delayed: whether to expand by "!"

        Returns:
            value of a variable as string
        """
        if self.extensions_enabled and key in self.dynamic_variables:
            return self._get_dynamic_variable(key)
        return self.variables.get(key)

    def set_variable(self, key, value_to_set):
        """
        Create a variable in the context.

        Args:
            key: variable name
            value_to_set: same as the name
        """
        self._variables[key] = value_to_set

    def delete_variable(self, key):
        """
        Delete a variable in the context.

        Args:
            key: variable name
        """
        self._variables[key] = ""

    @property
    def history(self):
        """
        Property.

        Returns:
            list of previously executed commands.
        """
        return self._history

    @history.setter
    def history(self, value_to_append):
        # TODO: convert to function
        if not self.history_enabled:
            return
        self._history.append(value_to_append)

    @property
    def echo(self) -> bool:
        """
        Property.

        Returns:
            boolean if echo is turned on
        """
        return self._echo

    @echo.setter
    def echo(self, echo_on: bool):
        self._echo = echo_on

    @property
    def prompt(self) -> bool:
        """
        Property.

        Returns:
            current prompt string
        """
        return self._prompt

    @prompt.setter
    def prompt(self, prompt_text: str):
        self._prompt = prompt_text
        self.set_variable("prompt", prompt_text)

    @staticmethod
    def _get_default_variables():  # noqa: WPS602, WPS605
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

    def _get_dynamic_variable(self, name: str) -> str:  # noqa: WPS212
        """
        Create and return a dynamic value for dynamic variable.

        Args:
            name: key name of a dynamic variable

        Returns:
            str: value of a dynamic variable
        """
        # pylint: disable=too-many-return-statements
        if name == "cd":
            return getcwd()
        if name == "date":
            return strftime("%x")
        if name == "time":
            return strftime("%X")
        if name == "random":
            return str(randint(0, DYNAMIC_RAND_MAX))  # noqa: S311
        if name == "errorlevel":
            return str(self.error_level)
        if name == "cmdextversion":
            return "2"
        if name == "cmdcmdline":
            return sys.argv[0]
        return ""

    def resolve_prompt(self) -> str:
        """
        Resolve a prompt string from the context.

        Returns:
            str: prompt string
        """
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
        return out


def get_context() -> dict:
    """
    Get a new Context instance with current working directory set.

    Returns:
        context.Context
    """
    cwd = getcwd().replace("/", "\\")
    return Context(cwd=cwd)
