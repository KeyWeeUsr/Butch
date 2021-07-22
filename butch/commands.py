"Module holding command-representing functions for their Batch names."

import sys
from locale import getlocale, setlocale, LC_NUMERIC, LC_CTYPE

from typing import List, Tuple
from inspect import getframeinfo, currentframe
from datetime import datetime
from enum import Enum
from os import remove, listdir, chdir, environ, makedirs, stat, statvfs, getcwd
from os.path import abspath, isdir, exists, join
from collections import defaultdict

from butch.context import Context
from butch.constants import (
    PATH_NOT_FOUND, PAUSE_TEXT, ENV_VAR_UNDEFINED, SYNTAX_INCORRECT,
    SURE, DELETE, PATH_EXISTS
)
from butch.outputs import CommandOutput
from butch.expansion import percent_expansion


class Command(Enum):
    "Enum of command types mapped to their textual representation."
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


def echo(params: List["Argument"], ctx: Context) -> None:
    "Batch: ECHO command."
    this = getframeinfo(currentframe()).function
    log = ctx.log.debug
    log("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)

    out = sys.stdout
    if ctx.collect_output:
        log("\t- should collect output")
        ctx.output = CommandOutput()
        out = ctx.output.stdout

    # pylint: disable=import-outside-toplevel
    from butch.help import print_help  # circular
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
        if first == "/?":
            print_help(cmd=Command.ECHO, file=out)
            return

    if not params_len:
        print(f"ECHO is {state[ctx.echo]}.", file=out)
        return

    print(*params, file=out)


def help_cmd(params: List["Argument"], ctx: Context) -> None:
    """Batch: HELP command."""
    this = getframeinfo(currentframe()).function
    log = ctx.log.debug
    log("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)

    out = sys.stdout
    if ctx.collect_output:
        log("\t- should collect output")
        ctx.output = CommandOutput()
        out = ctx.output.stdout

    cmd_map = get_reverse_cmd_map()
    # pylint: disable=import-outside-toplevel
    from butch.help import print_help  # circular
    params = [
        percent_expansion(line=param.value, ctx=ctx)
        for param in params
    ]
    if not params:
        print_help(cmd=Command.HELP, file=out)

    print_help(cmd=cmd_map.get(params[0].lower(), Command.UNKNOWN), file=out)


def _print_all_variables(ctx: Context) -> None:
    for key, val in ctx.variables.items():
        print(f"{key}={val}", file=sys.stdout)


def _print_single_variable(key: str, ctx: Context) -> None:
    value = ctx.get_variable(key)
    if not value:
        print(ENV_VAR_UNDEFINED, file=sys.stdout)
        return
    print(f"{key}={value}", file=sys.stdout)


def _delete_single_variable(key: str, ctx: Context) -> None:
    ctx.delete_variable(key=key)


def set_cmd(params: List["Argument"], ctx: Context) -> None:
    "Batch: SET command."
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    # pylint: disable=import-outside-toplevel
    from butch.help import print_help  # circular

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
    ctx.set_variable(key=left, value_to_set=right)


def setlocal(params: list, ctx: Context) -> None:
    "Batch: SETLOCAL command."
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    # pylint: disable=import-outside-toplevel
    from butch.help import print_help  # circular

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


# pylint: disable=invalid-name
def cd(params: list, ctx: Context) -> None:
    "Batch: CD command."
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    # pylint: disable=import-outside-toplevel
    from butch.help import print_help  # circular

    params_len = len(params)
    if not params:
        # linux
        chdir(environ.get("HOME"))
        # windows
        return

    params = [param.value for param in params]
    first = params[0]
    if params_len == 1 and first == "/?":
        print_help(cmd=Command.CD)
        return

    try:
        chdir(first)
    except FileNotFoundError:
        ctx.error_level = 1
        print(PATH_NOT_FOUND, file=sys.stdout)


def prompt(params: list, ctx: Context) -> None:
    "Batch: PROMPT command."
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    # pylint: disable=import-outside-toplevel
    from butch.help import print_help  # circular
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
    "Batch: TITLE command."
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    # pylint: disable=import-outside-toplevel
    from butch.help import print_help  # circular
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

    # pylint: disable=unreachable
    # Windows
    import ctypes
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.SetConsoleTitleW(text)
    error = ctypes.get_last_error()
    if error:
        raise ctypes.WinError(error)


def pause(params: list, ctx: Context) -> None:
    "Batch: PAUSE command."
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    # pylint: disable=import-outside-toplevel
    from butch.help import print_help  # circular
    first = params[0] if params else ""
    if first == "/?":
        print_help(cmd=Command.PAUSE)
        return

    input(PAUSE_TEXT)


def exit_cmd(params: list, ctx: Context) -> None:
    "Batch: EXIT command."
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)
    ctx.error_level = 0

    # pylint: disable=import-outside-toplevel
    from butch.help import print_help  # circular
    params_len = len(params)
    if not params_len:
        sys.exit(0)
        return

    params = [param.value for param in params]
    first = params[0]
    if first == "/?":
        print_help(cmd=Command.EXIT)
        return

    if "/B" in params:
        params.remove("/B")

    ctx.error_level = int(params[0])
    sys.exit(ctx.error_level)


def delete(params: List["Argument"], ctx: Context) -> None:
    "Batch: DEL/ERASE command."
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)

    # pylint: disable=import-outside-toplevel
    from butch.help import print_help  # circular
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
            print_help(cmd=Command.DELETE)
            return
        path = abspath(first)
        if not exists(path):
            os_path = path.replace("/", "\\")
            print(f"Could Not Find {os_path}")
            ctx.error_level = 0
            return

    # higher priority than quiet (/p /q = prompt)
    prompt_for_all = False
    quiet = False
    for item in params:
        low = item.lower()
        if low == "/p":
            prompt_for_all = True
        elif low == "/q":
            quiet = True

    # for multiple paths "not found" or error level setting is skipped
    for param in params:
        path = abspath(param)
        if not exists(path):
            continue

        os_path = path.replace("/", "\\")
        if isdir(param):
            answer = ""
            if prompt_for_all or not quiet:
                text = f"{os_path}\\*, {SURE}"
                if ctx.piped:
                    answer = ctx.output.stdout.read(1).decode("utf-8")
                    print(f"{text} {answer}")
                else:
                    answer = input(f"{text} ").lower()
            if answer != "y":
                continue
            for file in listdir(param):
                remove(join(path, file))
            return
        if prompt_for_all:
            answer = ""
            text = f"{os_path}, {DELETE}"
            if ctx.piped:
                answer = ctx.output.stdout.read(1).decode("utf-8")
                print(f"{text} {answer}")
            else:
                answer = input(text).lower()
            if answer != "y":
                continue
        remove(path)
    ctx.error_level = 0
    ctx.piped = False


def create_folder(params: List["Argument"], ctx: Context) -> None:
    "Batch: MKDIR/MD command."
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)

    # pylint: disable=import-outside-toplevel
    from butch.help import print_help  # circular
    params = [
        percent_expansion(line=param.value, ctx=ctx)
        for param in params
    ]
    params_len = len(params)

    if not params_len:
        # do this also for piped input as mkdir does not care about pipes
        # echo hello | mkdir -> syntax incorrect
        print(SYNTAX_INCORRECT)
        ctx.error_level = 1
        return

    if params_len == 1:
        first = params[0]
        if first.lower() == "/?":
            print_help(cmd=Command.MKDIR)
            return
        first = first.replace("\\", "/")
        path = abspath(first)
        try:
            makedirs(path)
        except FileExistsError:
            print(PATH_EXISTS.format(first))
            ctx.error_level = 1
        return

    failed = False
    for param in params:
        path = abspath(param.replace("\\", "/"))

        try:
            makedirs(param)
        except FileExistsError:
            print(PATH_EXISTS.format(param))
            failed = True

    ctx.error_level = failed
    ctx.piped = False


def _get_listdir_lines(folder: str, ctx: Context) -> list:
    files = listdir()
    files.sort()

    files = [".", ".."] + files

    tmp = []
    count = defaultdict(int)

    old_locale = getlocale(LC_NUMERIC)
    setlocale(LC_NUMERIC, getlocale(LC_CTYPE))
    for item in files:
        raw = stat(item)
        date = datetime.fromtimestamp(raw.st_ctime)
        time = date.strftime("%X")
        date = date.strftime("%x")
        is_dir = isdir(item)
        dir_text = "<DIR>".ljust(14) if is_dir else ""
        size = raw.st_size

        if is_dir:
            count["total_size"] += size
            size = ""
        else:
            size = "{0:n}".format(size).rjust(14)

        count["folders" if is_dir else "files"] += 1
        tmp.append(f"{date}  {time}    {dir_text}  {size} {item}")

    prefix = [
        " Volume in drive <NYI> has no label.",
        " Volume Serial Number is <NYI>",
        "",
        f" Directory of {ctx.cwd}",
        ""
    ]

    free_bytes = statvfs(folder)
    free_bytes = "{0:n}".format(
        free_bytes.f_frsize * free_bytes.f_bavail
    ).rjust(14)
    file_count = str(count["files"]).rjust(17)
    folder_count = str(count["folders"]).rjust(18)
    used_bytes = "{0:n}".format(count['total_size']).rjust(14)
    suffix = [
        f"{file_count} File(s){used_bytes} bytes",
        f"{folder_count} Dir(s){free_bytes} bytes free",
    ]
    setlocale(LC_NUMERIC, old_locale)
    return prefix + tmp + suffix


def list_folder(params: List["Argument"], ctx: Context) -> None:
    "Batch: DIR command."
    this = getframeinfo(currentframe()).function
    ctx.log.debug("<cmd: %-8.8s>, params: %r, ctx: %r", this, params, ctx)

    # pylint: disable=import-outside-toplevel
    from butch.help import print_help  # circular
    params = [
        percent_expansion(line=param.value, ctx=ctx)
        for param in params
    ]
    params_len = len(params)

    if not params_len:
        # show current directory list
        lines = _get_listdir_lines(folder=getcwd(), ctx=ctx)
        print("\n".join(lines))
        ctx.error_level = 0
        return

    raise NotImplementedError()


def get_cmd_map():
    "Get mapping of CommandType into its functions for execution."
    return {
        Command.ECHO: echo,
        Command.CD: cd,
        Command.SET: set_cmd,
        Command.PROMPT: prompt,
        Command.TITLE: title,
        Command.PAUSE: pause,
        Command.EXIT: exit_cmd,
        Command.SETLOCAL: setlocal,
        Command.DELETE: delete,
        Command.ERASE: delete,
        Command.HELP: help_cmd,
        Command.MKDIR: create_folder,
        Command.MD: create_folder,
        Command.DIR: list_folder
    }


def get_reverse_cmd_map():
    "Get reverse CommandType mapping for resolving a string into CommandType."
    return {
        getattr(Command, item).value: getattr(Command, item)
        for item in dir(Command)
        if isinstance(getattr(Command, item), Command)
        and item != Command.UNKNOWN.name
    }


def parse(values: str) -> Tuple[Command, list]:
    "Parse a string into a command."
    cmd, *params = values.split(" ")
    unk = Command.UNKNOWN.name

    cmds = {
        getattr(Command, item).value: getattr(Command, item)
        for item in dir(Command)
        if isinstance(getattr(Command, item), Command) and item != unk
    }

    if cmd in cmds:
        return (cmds[cmd], params)
    return (Command.UNKNOWN, [cmd])
