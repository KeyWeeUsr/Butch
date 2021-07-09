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
    params_len = len(params)
    state = {True: "on", False: "off"}
    state_rev = {val: key for key, val in state.items()}

    if params_len == 1:
        first = params[0].lower()
        if first in ("on", "off"):
            ctx.echo = state_rev[first]
            return

    if not params_len:
        print(f"ECHO is {state[ctx.echo]}.")
        return

    print(*params)


def set_cmd(params: list, ctx: Context) -> None:
    ctx.log.debug("SET cmd params: %r", params)
    # TODO: stored as case-sensitive, access by insensitive
    params_len = len(params)
    if not params_len:
        for key, val in ctx.variables.items():
            # TODO: case-sensitive key should be printed
            print(f"{key}={val}")
        return

    # >1 values are ignored
    param = params[0]
    if "=" not in param:
        # TODO: case-sensitive key should be printed
        key = param
        print(f"{key}={ctx.get_variable(key)}")
        return

    left, right = param.split("=")
    if left and not right:
        ctx.delete_variable(left.lower())
        return

    ctx.set_variable(left.lower(), right)


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
