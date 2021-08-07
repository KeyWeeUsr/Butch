"""Module for global or local (command) state related classes and functions."""

import sys
from logging import RootLogger
from os import chdir, getcwd
from os.path import abspath, exists, isdir
from random import randint
from tempfile import gettempdir
from time import strftime

from butch.logger import get_logger
from butch.inputs import CommandInput
from butch.outputs import CommandOutput

PROMPT_KEY = "prompt"
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


class BadContextKey(Exception):
    """Raised when incorrect keyword argument is specified for Context."""


class Context:  # noqa: WPS214,WPS338
    """
    Holds the state for the interpreter.

    The in-between command state and the overall, global state of the language
    interpreter.
    """

    # pylint: disable=too-many-instance-attributes,too-many-public-methods

    _cwd: str
    _variables: dict
    _error_level: int
    _extensions_enabled: bool
    _delayed_expansion_enabled: bool
    _dynamic_variables: list = [
        "cd",
        "cmdcmdline",
        "cmdextversion",
        "date",
        "errorlevel",
        "random",
        "time"
    ]
    _history: list
    _history_enabled: bool
    _pushd_history: list
    _echo: bool
    _prompt: str
    _input: CommandInput
    _output: CommandOutput
    _collect_output: bool
    _piped: bool
    _inputted: bool
    _logger: RootLogger

    def __init__(self, **kwargs):
        """
        Initialize Context with default and dynamic properties.

        Args:
            kwargs: pairs to attempt to setattr() into properties

        Raises:
            BadContextKey: disallow setting custom properties from __init__
        """
        self._collect_output = False
        self._cwd = getcwd()
        self._delayed_expansion_enabled = False
        self._echo = True
        self._error_level = 0
        self._extensions_enabled = True
        self._history = []
        self._history_enabled = True
        self._pushd_history = []
        self._logger = get_logger()
        self._input = None
        self._output = None
        self._piped = False
        self._inputted = False
        self._variables = self._get_default_variables()

        # dynamic
        self._prompt = self._variables.get(PROMPT_KEY, "")

        for key, kwarg in kwargs.items():
            if key not in dir(Context):
                raise BadContextKey(f"Bad key: '{key}' (ignored)")
            setattr(self, f"_{key}", kwarg)

    def __repr__(self):
        """Stringify the context.

        Returns:
            dict-like style of specific context properties
        """
        keys = (
            "cwd",
            "delayed_expansion_enabled",
            "dynamic_variables",
            "echo",
            "error_level",
            "extensions_enabled",
            "history",
            "history_enabled",
            PROMPT_KEY,
            "variables"
        )
        return str({key: getattr(self, key) for key in keys})

    @property
    def log(self):
        """
        Property.

        Returns:
            reference to the Butch's logger.
        """
        return self._logger

    @property
    def cwd(self):
        """
        Property.

        Returns:
            current working directory.
        """
        return self._cwd

    @cwd.setter
    def cwd(self, new_cwd: str):
        chdir(new_cwd)
        self._cwd = getcwd()

    @property
    def error_level(self):
        """
        Property.

        Returns:
            current error level of a script.
        """
        return self._error_level

    @error_level.setter
    def error_level(self, level):
        self._error_level = level

    @property
    def piped(self):
        """
        Property.

        Returns:
            flag whether the previous command was piped.
        """
        return self._piped

    @piped.setter
    def piped(self, enabled):
        self._piped = enabled

    @property
    def inputted(self):
        """
        Property.

        Returns:
            flag whether the input was read from STDIN.
        """
        return self._inputted

    @inputted.setter
    def inputted(self, enabled):
        self._inputted = enabled

    @property
    def collect_output(self):
        """
        Property.

        Returns:
            flag whether to collect output to pipe or redirection.
        """
        return self._collect_output

    @collect_output.setter
    def collect_output(self, collected):
        self._collect_output = collected

    @property
    def output(self):
        """
        Property.

        Returns:
            stored output / passed input if piped or redirected.
        """
        return self._output

    @output.setter
    def output(self, out):
        self._output = out

    @property
    def input(self):
        """
        Property.

        Returns:
            stored input / passed input if redirected.
        """
        return self._input

    @input.setter
    def input(self, input_value):
        self._input = input_value

    @property
    def pushd_history(self):
        """
        Get full pushd history.

        Returns:
            list with all folders in the pushd history
        """
        return self._pushd_history

    def push_folder(self, path: str) -> None:
        """
        Add new path to pushd history for popd retrieval and chdir() to it.

        Args:
            path (str): path to append to the PUSHD folder history.
        """
        if not isdir(path):
            self.error_level = 1
            return

        if exists(path):
            self._pushd_history.append(abspath(path))
        self.cwd = path

    def pop_folder(self) -> str:
        """
        Pop the latest folder from pushd history and return it.

        Returns:
            the most recent item from the PUSHD folder history.
        """
        return self._pushd_history.pop(0)

    @property
    def extensions_enabled(self):
        """
        Property.

        Returns:
            Batch extensions flag.
        """
        return self._extensions_enabled

    @extensions_enabled.setter
    def extensions_enabled(self, enabled):
        self._extensions_enabled = enabled

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
        self.set_variable(key=PROMPT_KEY, value_to_set=prompt_text)

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
            PROMPT_KEY: f"{PROMPT_DRIVE_PATH}{PROMPT_GREATER}",
            "sessionname": None,
            "systemdrive": None,
            "systemroot": None,
            "temp": gettempdir(),
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
                out += self.cwd.replace("\\", "/")
        return out


def get_context() -> dict:
    """
    Get a new Context instance with current working directory set.

    Returns:
        context.Context
    """
    cwd = getcwd().replace("/", "\\")
    return Context(cwd=cwd)
