from enum import Enum
from context import Context


class Command(Enum):
    UNKNOWN = "<unknown>"
    ECHO = "echo"
    CD = "cd"
    SET = "set"


def echo(params: list, ctx: Context) -> None:
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

    chdir(params[0])


CMD_MAP = {
    Command.ECHO: echo,
    Command.CD: cd,
    Command.SET: set_cmd
}
