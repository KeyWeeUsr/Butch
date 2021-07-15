import sys
import json
from typing import List
from inspect import getframeinfo, currentframe
from enum import Enum
from ast import literal_eval
from context import Context
from constants import PATH_NOT_FOUND, PAUSE_TEXT


class Command(Enum):
    UNKNOWN = "<unknown>"
    ECHO = "echo"
    CD = "cd"
    SET = "set"
    PROMPT = "prompt"
    TITLE = "title"
    PAUSE = "pause"
    EXIT = "exit"
    SETLOCAL = "setlocal"


def echo(params: List["Argument"], ctx: Context) -> None:
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)

    from parser import parse_variables
    params = parse_variables(values=[param.value for param in params], ctx=ctx)
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


def set_cmd(params: List["Argument"], ctx: Context) -> None:
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
    quoted = param.quoted
    value = param.value
    if quoted:
        ctx.log.debug("\t- quoted variable")
        value = value[1:-1]
    if "=" not in value:
        ctx.log.debug("\t- single variable print")
        _print_single_variable(key=value, ctx=ctx)
        return

    left, right = value.split("=")
    if left and not right:
        ctx.log.debug("\t- single variable delete")
        _delete_single_variable(key=left.lower(), ctx=ctx)
        return

    left = left.lower()
    ctx.log.debug("\t- single variable create: %r, %r", left, right)
    ctx.set_variable(key=left, value=right)


def setlocal(params: list, ctx: Context) -> None:
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    # TODO: stored as case-sensitive, access by insensitive
    params_len = len(params)
    if not params_len:
        # copy all variables to new session, restore old state with endlocal
        return

    value = [item.lower() for item in set(params)][0]
    if value == "enabledelayedexpansion":
        ctx.delayed_expansion_enabled = True
        return

    if value == "disabledelayedexpansion":
        ctx.delayed_expansion_enabled = False
        return

    if value == "enableextensions":
        ctx.extensions_enabled = True
        return

    if value == "disableextensions":
        ctx.extensions_enabled = False
        return


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
        print(PATH_NOT_FOUND)


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


def title(params: list, ctx: Context) -> None:
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    params_len = len(params)
    if not params_len:
        print()
        return

    # Linux
    text = params[0]
    sys.stdout.write(f"\x1b]2;{text}\x07")
    return

    # Windows
    import ctypes
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel32.SetConsoleTitleW(text)
    error = ctypes.get_last_error()
    if error:
        raise ctypes.WinError(error)


def pause(params: list, ctx: Context) -> None:
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    input(PAUSE_TEXT)


def exit_cmd(params: list, ctx: Context) -> None:
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    params_len = len(params)
    if not params_len:
        print()
        return

    if "/B" in params:
        params.remove("/B")

    ctx.error_level = int(params[0])
    sys.exit(ctx.error_level)


def get_cmd_map():
    return {
        Command.ECHO: echo,
        Command.CD: cd,
        Command.SET: set_cmd,
        Command.PROMPT: prompt,
        Command.TITLE: title,
        Command.PAUSE: pause,
        Command.EXIT: exit_cmd,
        Command.SETLOCAL: setlocal
    }

def get_reverse_cmd_map():
    return {
        getattr(Command, item).value: getattr(Command, item)
        for item in dir(Command)
        if isinstance(getattr(Command, item), Command)
        and item != Command.UNKNOWN.name
    }
