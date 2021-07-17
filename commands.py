import sys
import json

from typing import List
from inspect import getframeinfo, currentframe
from enum import Enum
from ast import literal_eval
from os import remove, listdir
from os.path import abspath, isdir, exists, join

from context import Context
from constants import (
    PATH_NOT_FOUND, PAUSE_TEXT, ENV_VAR_UNDEFINED, SYNTAX_INCORRECT,
    SURE
)


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
    DELETE = "del"


def echo(params: List["Argument"], ctx: Context) -> None:
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)

    from parser import percent_expansion
    from help import print_help
    params = [
        percent_expansion(line=param.value, ctx=ctx)
        for param in params
    ]
    params_len = len(params)
    state = {True: "on", False: "off"}
    state_rev = {val: key for key, val in state.items()}

    if params_len == 1:
        first = params[0].lower()
        if first in ("on", "off"):
            ctx.echo = state_rev[first]
            return
        elif first == "/?":
            print_help(cmd=Command.ECHO)
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
    value = ctx.get_variable(key)
    if not value:
        print(ENV_VAR_UNDEFINED)
        return
    print(f"{key}={value}")


def _delete_single_variable(key: str, ctx: Context) -> None:
    ctx.delete_variable(key=key)


def set_cmd(params: List["Argument"], ctx: Context) -> None:
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    from help import print_help
    # TODO: stored as case-sensitive, access by insensitive
    params_len = len(params)
    if not params_len:
        _print_all_variables(ctx=ctx)
        return

    param = params[0]
    value = param.value
    if params_len == 1 and value == "/?":
        print_help(cmd=Command.SET)
        return

    # >1 values are ignored
    quoted = param.quoted
    value = param.value
    if quoted:
        ctx.log.debug("\t- quoted variable")
        value = value[1:value.rfind('"')]
    if "=" not in value:
        ctx.log.debug("\t- single variable print: %r", value)
        _print_single_variable(key=value, ctx=ctx)
        return

    left, right = value.split("=")
    if left and not right:
        ctx.log.debug("\t- single variable delete: %r", left)
        _delete_single_variable(key=left.lower(), ctx=ctx)
        return

    left = left.lower()
    ctx.log.debug("\t- single variable create: %r, %r", left, right)
    ctx.set_variable(key=left, value=right)


def setlocal(params: list, ctx: Context) -> None:
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    from help import print_help
    # TODO: stored as case-sensitive, access by insensitive
    params_len = len(params)
    if not params_len:
        # copy all variables to new session, restore old state with endlocal
        return

    if params_len == 1 and params[0] == "/?":
        print_help(cmd=Command.SETLOCAL)
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
    from help import print_help
    params_len = len(params)
    if not params:
        # linux
        chdir(environ.get("HOME"))
        # windows
        ## do nothing
        return

    first = params[0]
    if params_len == 1 and first == "/?":
        print_help(cmd=Command.CD)
        return

    try:
        chdir(first)
    except FileNotFoundError:
        ctx.error_level = 1
        print(PATH_NOT_FOUND)


def prompt(params: list, ctx: Context) -> None:
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    from help import print_help
    params_len = len(params)
    if not params_len:
        print()
        return

    first = params[0]
    if params_len == 1 and first == "/?":
        print_help(cmd=Command.PROMPT)
        return
    text = first
    ctx.prompt = text


def title(params: list, ctx: Context) -> None:
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    from help import print_help
    params_len = len(params)
    if not params_len:
        print()
        return

    first = params[0]
    if params_len == 1 and first == "/?":
        print_help(cmd=Command.TITLE)
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

    from help import print_help
    first = params[0] if params else ""
    if first == "/?":
        print_help(cmd=Command.PAUSE)
        return

    input(PAUSE_TEXT)


def exit_cmd(params: list, ctx: Context) -> None:
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    from help import print_help
    params_len = len(params)
    if not params_len:
        print()
        return

    first = params[0]
    if first == "/?":
        print_help(cmd=Command.EXIT)
        return

    if "/B" in params:
        params.remove("/B")

    ctx.error_level = int(params[0])
    sys.exit(ctx.error_level)


def delete(params: List["Argument"], ctx: Context) -> None:
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)

    from parser import percent_expansion
    from help import print_help
    params = [
        percent_expansion(line=param.value, ctx=ctx)
        for param in params
    ]
    params_len = len(params)

    if not params_len:
        print(SYNTAX_INCORRECT)
        ctx.error_level = 1
        return

    if params_len == 1:
        first = params[0]
        if first.lower() == "/?":
            print_help(cmd=Command.ECHO)
            return
        path = abspath(first)
        if not exists(path):
            os_path = path.replace('/', '\\')
            print(f"Could Not Find {os_path}")
            ctx.error_level = 0
            return

    # for multiple paths "not found" or error level setting is skipped
    for param in params:
        path = abspath(param)
        if not exists(path):
            continue

        os_path = path.replace('/', '\\')
        if isdir(param):
            answer = input(f"{os_path}\*, {SURE} ")
            if answer.lower() != "y":
                continue
            for file in listdir(param):
                remove(join(path, file))
            return
        remove(path)
    ctx.error_level = 0


def get_cmd_map():
    return {
        Command.ECHO: echo,
        Command.CD: cd,
        Command.SET: set_cmd,
        Command.PROMPT: prompt,
        Command.TITLE: title,
        Command.PAUSE: pause,
        Command.EXIT: exit_cmd,
        Command.SETLOCAL: setlocal,
        Command.DELETE: delete
    }

def get_reverse_cmd_map():
    return {
        getattr(Command, item).value: getattr(Command, item)
        for item in dir(Command)
        if isinstance(getattr(Command, item), Command)
        and item != Command.UNKNOWN.name
    }
