"""
Module for CommandType class to prevent circular imports.
"""
from enum import Enum


class CommandType(Enum):
    """
    Enum of command types mapped to their textual representation.
    """
    # noqa: WPS115
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
    CLS = "cls"
    DATE = "date"
    RMDIR = "rmdir"
    RD = "rd"
    TYPE = "type"
    PATH = "path"
    REM = "rem"
    PUSHD = "pushd"
    POPD = "popd"
