from enum import Enum
from context import Context
from constants import PATH_NOT_FOUND


class Command(Enum):
    UNKNOWN = "<unknown>"
    ECHO = "echo"
    CD = "cd"
    SET = "set"


def echo(params: list, ctx: Context) -> None:
    from parser import parse_variables
    params = parse_variables(values=params, ctx=ctx)
    print(*params)


def set_cmd(params: list, ctx: Context) -> None:
    pass


def _safe_chdir(*args):
    try:
        chdir(*args)
    except FileNotFoundError:
        print("The system cannot find the path specified.")


def cd(params: list, ctx: Context) -> None:
    from os import chdir, environ
    if not params:
        # linux
        chdir(environ.get("HOME"))
        # windows
        ## do nothing
        return

    try:
        chdir(params[0])
    except FileNotFoundError:
        ctx.error_level = 1
        print("The system cannot find the path specified.")


def get_cmd_map():
    return {
        Command.ECHO: echo,
        Command.CD: cd,
        Command.SET: set_cmd
    }
