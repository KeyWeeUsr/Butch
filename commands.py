from inspect import getframeinfo, currentframe
from enum import Enum
from context import Context
from constants import PATH_NOT_FOUND


class Command(Enum):
    UNKNOWN = "<unknown>"
    ECHO = "echo"
    CD = "cd"
    SET = "set"
    PROMPT = "prompt"


def echo(params: list, ctx: Context) -> None:
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

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


def _print_all_variables(ctx: Context) -> None:
    for key, val in ctx.variables.items():
        # TODO: case-sensitive key should be printed
        print(f"{key}={val}")


def _print_single_variable(key: str, ctx: Context) -> None:
    # TODO: case-sensitive key should be printed
    print(f"{key}={ctx.get_variable(key)}")


def _delete_single_variable(key: str, ctx: Context) -> None:
    ctx.delete_variable(key)


def set_cmd(params: list, ctx: Context) -> None:
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    # TODO: stored as case-sensitive, access by insensitive
    params_len = len(params)
    if not params_len:
        _print_all_variables(ctx=ctx)
        return

    # >1 values are ignored
    param = params[0]
    if "=" not in param:
        _print_single_variable(key=param, ctx=ctx)
        return

    left, right = param.split("=")
    if left and not right:
        _delete_single_variable(key=left.lower(), ctx=ctx)
        return

    ctx.set_variable(key=left.lower(), value=right)


def _safe_chdir(*args):
    try:
        chdir(*args)
    except FileNotFoundError:
        print("The system cannot find the path specified.")


def cd(params: list, ctx: Context) -> None:
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

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


def prompt(params: list, ctx: Context) -> None:
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    params_len = len(params)
    if not params_len:
        print()
        return

    text = params[0]
    ctx.prompt = text


def get_cmd_map():
    return {
        Command.ECHO: echo,
        Command.CD: cd,
        Command.SET: set_cmd,
        Command.PROMPT: prompt
    }
