from enum import Enum


class Command(Enum):
    UNKNOWN = "<unknown>"
    ECHO = "echo"
    CD = "cd"


def echo(params: list) -> None:
    print(*params)


def _safe_chdir(*args):
    try:
        chdir(*args)
    except FileNotFoundError:
        print("The system cannot find the path specified.")


def cd(params: list) -> None:
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
    Command.CD: cd
}
