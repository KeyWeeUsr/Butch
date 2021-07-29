"""Module for CommandType class to prevent circular imports."""
import enum


class CommandType(enum.Enum):
    """Enum of command types mapped to their textual representation."""

    UNKNOWN = "<unknown>"
    ECHO = "echo"
    CD = "cd"
    SET = "set"
    PROMPT = "prompt"
    TITLE = "title"
    PAUSE = "pause"
    EXIT = "exit"
    SETLOCAL = "setlocal"
    DELETE = "del"
    ERASE = "erase"
    HELP = "help"
    MKDIR = "mkdir"
    MD = "md"
    DIR = "dir"
    CLS = "cls"  # noqa: WPS117
    DATE = "date"
    RMDIR = "rmdir"
    RD = "rd"
    TYPE = "type"
    PATH = "path"
    REM = "rem"
    PUSHD = "pushd"
    POPD = "popd"
    TIME = "time"
