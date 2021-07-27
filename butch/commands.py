"""Module holding command-representing functions for their Batch names."""

import sys
import ctypes
from locale import LC_CTYPE, LC_NUMERIC, getlocale, setlocale

from typing import List, Tuple
from datetime import datetime
from os import environ, getcwd, listdir, makedirs, remove, stat, statvfs
from os.path import abspath, exists, isdir, join
from collections import defaultdict
from shutil import rmtree

from butch.context import Context
from butch.constants import (
    ACCESS_DENIED, DELETE, DIR_INVALID, DIR_NONEMPTY, ENV_VAR_UNDEFINED,
    ERROR_PROCESSING, FILE_NOT_FOUND, PATH_EXISTS, PATH_NOT_FOUND, PAUSE_TEXT,
    SURE, SYNTAX_INCORRECT
)
from butch.outputs import CommandOutput
from butch.expansion import percent_expansion
from butch.commandtype import CommandType
from butch.help import print_help
from butch.tokens import Argument


DIR_FORMAT_TOTAL_SIZE_RJUST = 14
DIR_FORMAT_FILE_COUNT_RJUST = 17
DIR_FORMAT_FOLDER_COUNT_RJUST = 18
DIR_FORMAT_FREE_BYTES_RJUST = 14
DIR_FORMAT_FOLDER_SYMBOL_LJUST = 14
DIR_FORMAT_FILE_BYTES_RJUST = 14


def what_func(func):
    def wrapper(*args, **kwargs):
        ctx = kwargs.get("ctx")
        params = kwargs.get("params")
        if ctx:
            ctx.log.debug(
                "<cmd: %-8.8s>, params: %r, ctx: %r",
                func.__name__, params, ctx
            )
        func(*args, **kwargs)
    return wrapper


@what_func
def echo(params: List[Argument], ctx: Context) -> None:
    """
    Batch: ECHO command.

    Must NOT set error level to 0.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    log = ctx.log.debug

    out = sys.stdout
    if ctx.collect_output:
        log("\t- should collect output")
        ctx.output = CommandOutput()
        out = ctx.output.stdout

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
            print_help(cmd=CommandType.ECHO, file=out)
            return

    if not params_len:
        print(f"ECHO is {state[ctx.echo]}.", file=out)
        return

    print(*params, file=out)


@what_func
def type_cmd(params: List[Argument], ctx: Context) -> None:
    """
    Batch: TYPE command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    log = ctx.log.debug

    out = sys.stdout
    if ctx.collect_output:
        log("\t- should collect output")
        ctx.output = CommandOutput()
        out = ctx.output.stdout

    params = [
        percent_expansion(line=param.value, ctx=ctx)
        for param in params
    ]
    params_len = len(params)

    if not params_len:
        print(SYNTAX_INCORRECT, file=sys.stdout)
        ctx.error_level = 1
        return

    if params_len == 1:
        first = params[0].lower()
        if first == "/?":
            print_help(cmd=CommandType.ECHO, file=out)
            return

        if isdir(first):
            print(ACCESS_DENIED, file=out)
            ctx.error_level = 1
            return

        if not exists(first):
            print(FILE_NOT_FOUND, file=out)
            ctx.error_level = 1
            return

        with open(first) as file:
            # TODO: big files chunking
            print(file.read(), file=out)
            return

    for idx, item_path in enumerate(params):
        print(item_path, file=out)

        if isdir(item_path):
            print(ACCESS_DENIED, file=out)
            print(ERROR_PROCESSING.format(item_path), file=out)
            ctx.error_level = 1
            continue

        if not exists(item_path):
            print(FILE_NOT_FOUND, file=out)
            print(ERROR_PROCESSING.format(item_path), file=out)
            ctx.error_level = 1
            continue

        for _ in range(2):
            print("\n", file=out)

        with open(item_path) as file:
            # TODO: big files chunking
            print(file.read(), file=out)
        # no trailing newline after files
        if idx != params_len - 1:
            print("\n", file=out)


@what_func
def path_cmd(params: List[Argument], ctx: Context) -> None:
    """
    Batch: PATH command.

    Must NOT set errorlevel.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    log = ctx.log.debug

    out = sys.stdout
    if ctx.collect_output:
        log("\t- should collect output")
        ctx.output = CommandOutput()
        out = ctx.output.stdout

    params = [
        percent_expansion(line=param.value, ctx=ctx)
        for param in params
    ]
    params_len = len(params)

    if not params_len:
        print(f"PATH={ctx.get_variable('PATH') or '(null)'}", file=sys.stdout)
        return

    first = params[0].lower()
    if first == "/?":
        print_help(cmd=CommandType.PATH, file=out)
        return

    if first == ";":
        ctx.delete_variable(key="PATH")
        return

    ctx.set_variable(key="PATH", value_to_set=" ".join(params))


@what_func
def pushd(params: List[Argument], ctx: Context) -> None:
    """
    Batch: PUSHD command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    log = ctx.log.debug

    out = sys.stdout
    if ctx.collect_output:
        log("\t- should collect output")
        ctx.output = CommandOutput()
        out = ctx.output.stdout

    params = [
        percent_expansion(line=param.value, ctx=ctx)
        for param in params
    ]
    params_len = len(params)

    if not params_len:
        return

    first = params[0].lower()
    if first == "/?":
        print_help(cmd=CommandType.PUSHD, file=out)
        return

    path = " ".join(params)
    try:
        ctx.push_folder(path=path)
    except FileNotFoundError:
        ctx.error_level = 1
        print(PATH_NOT_FOUND, file=sys.stdout)


@what_func
def popd(params: List[Argument], ctx: Context) -> None:
    """
    Batch: POPD command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    log = ctx.log.debug

    out = sys.stdout
    if ctx.collect_output:
        log("\t- should collect output")
        ctx.output = CommandOutput()
        out = ctx.output.stdout

    params = [
        percent_expansion(line=param.value, ctx=ctx)
        for param in params
    ]

    first = params[0].lower() if params else ""
    if first == "/?":
        print_help(cmd=CommandType.POPD, file=out)
        return

    try:
        ctx.cwd = ctx.pop_folder()
    except FileNotFoundError:
        log("Folder for POPD not found, ignoring.")
    except IndexError:
        log("Empty popd history, ignoring.")


@what_func
def help_cmd(params: List[Argument], ctx: Context) -> None:
    """
    Batch: HELP command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    log = ctx.log.debug

    out = sys.stdout
    if ctx.collect_output:
        log("\t- should collect output")
        ctx.output = CommandOutput()
        out = ctx.output.stdout

    cmd_map = get_reverse_cmd_map()
    params = [
        percent_expansion(line=param.value, ctx=ctx)
        for param in params
    ]
    if not params:
        print_help(cmd=CommandType.HELP, file=out)

    print_help(
        cmd=cmd_map.get(params[0].lower(), CommandType.UNKNOWN), file=out
    )


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


@what_func
def set_cmd(params: List[Argument], ctx: Context) -> None:
    """
    Batch: SET command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    ctx.error_level = 0

    params_len = len(params)
    if not params_len:
        _print_all_variables(ctx=ctx)
        return

    param = params[0]
    value = param.value
    if params_len == 1 and value == "/?":
        print_help(cmd=CommandType.SET)
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


@what_func
def setlocal(params: list, ctx: Context) -> None:
    """
    Batch: SETLOCAL command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    ctx.error_level = 0

    params_len = len(params)
    if not params_len:
        # copy all variables to new session, restore old state with endlocal
        return

    if params_len == 1 and params[0] == "/?":
        print_help(cmd=CommandType.SETLOCAL)
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
@what_func
def cd(params: list, ctx: Context) -> None:
    """
    Batch: CD command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    ctx.error_level = 0

    params_len = len(params)
    if not params:
        # linux
        ctx.cwd = environ.get("HOME")
        # windows
        return

    params = [
        percent_expansion(line=param.value, ctx=ctx)
        for param in params
    ]
    first = params[0]
    if params_len == 1 and first == "/?":
        print_help(cmd=CommandType.CD)
        return

    try:
        ctx.cwd = first
    except FileNotFoundError:
        ctx.error_level = 1
        print(PATH_NOT_FOUND, file=sys.stdout)


@what_func
def prompt(params: list, ctx: Context) -> None:
    """
    Batch: PROMPT command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    ctx.error_level = 0

    params_len = len(params)
    if not params_len:
        print()
        return

    first = params[0]
    if params_len == 1 and first == "/?":
        print_help(cmd=CommandType.PROMPT)
        return
    text = first
    ctx.prompt = text


@what_func
def title(params: list, ctx: Context) -> None:
    """
    Batch: TITLE command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    ctx.error_level = 0

    params_len = len(params)
    if not params_len:
        print()
        return

    first = params[0]
    if params_len == 1 and first == "/?":
        print_help(cmd=CommandType.TITLE)
        return

    # Linux
    text = params[0]
    sys.stdout.write(f"\x1b]2;{text}\x07")
    return

    # pylint: disable=unreachable
    # Windows
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.SetConsoleTitleW(text)
    error = ctypes.get_last_error()
    if error:
        raise ctypes.WinError(error)


@what_func
def date(params: list, ctx: Context) -> None:
    """
    Batch: DATE command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    ctx.error_level = 0

    first = params[0].value if params else ""
    if first == "/?":
        print_help(cmd=CommandType.DATE)
        return

    now = datetime.now()
    if first.upper() == "/T":
        # should match the locale format
        print(now.strftime("%x"))
        return

    now = now.strftime("%a %x")
    print(f"The current date is: {now}")
    print("Enter the new date: (mm-dd-yy)")
    print("Setting the date is not implemented, use /T", file=sys.stderr)
    input()


@what_func
def pause(params: list, ctx: Context) -> None:
    """
    Batch: PAUSE command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    ctx.error_level = 0

    first = params[0] if params else ""
    if first.value == "/?":
        print_help(cmd=CommandType.PAUSE)
        return

    input(PAUSE_TEXT)


@what_func
def clear_screen(params: list, ctx: Context) -> None:
    """
    Batch: CLS command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    ctx.error_level = 0

    first = params[0] if params else ""
    if first.value == "/?":
        print("here")
        print_help(cmd=CommandType.CLS)
        return

    print("\033c" if "DEBUG" not in environ else "<clear>")


@what_func
def exit_cmd(params: list, ctx: Context) -> None:
    """
    Batch: EXIT command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    ctx.error_level = 0

    params_len = len(params)
    if not params_len:
        sys.exit(0)
        return

    params = [param.value for param in params]
    first = params[0]
    if first == "/?":
        print_help(cmd=CommandType.EXIT)
        return

    if "/B" in params:
        params.remove("/B")

    ctx.error_level = int(params[0])
    sys.exit(ctx.error_level)


@what_func
def delete(params: List[Argument], ctx: Context) -> None:
    """
    Batch: DEL/ERASE command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements

    params = [
        percent_expansion(line=param.value, ctx=ctx)
        for param in params
    ]
    params_len = len(params)

    if not params_len:
        print(SYNTAX_INCORRECT, file=sys.stdout)
        ctx.error_level = 1
        return

    if params_len == 1:
        first = params[0]
        if first.lower() == "/?":
            print_help(cmd=CommandType.DELETE)
            return
        file_path = abspath(first)
        if not exists(file_path):
            os_path = file_path.replace("/", "\\")
            print(f"Could Not Find {os_path}")
            ctx.error_level = 0
            return

    # higher priority than quiet (/p /q = prompt)
    prompt_for_all = False
    quiet = False
    for param in params:
        low = param.lower()
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
                    answer = ctx.output.stdout.read(1)
                    print(f"{text} {answer}")
                else:
                    answer = input(f"{text} ").lower()
            if answer != "y":
                continue
            for file_item in listdir(param):
                remove(join(path, file_item))
            return
        if prompt_for_all:
            answer = ""
            text = f"{os_path}, {DELETE}"
            if ctx.piped:
                answer = ctx.output.stdout.read(1)
                print(f"{text} {answer}")
            else:
                answer = input(text).lower()
            if answer != "y":
                continue
        remove(path)
    ctx.error_level = 0
    ctx.piped = False


@what_func
def create_folder(params: List[Argument], ctx: Context) -> None:
    """
    Batch: MKDIR/MD command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
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
            print_help(cmd=CommandType.MKDIR)
            return
        first = first.replace("\\", "/")
        dir_path = abspath(first)
        try:
            makedirs(dir_path)
        except FileExistsError:
            print(PATH_EXISTS.format(first))
            ctx.error_level = 1
        return

    failed = False
    for param in params:
        try:
            makedirs(param)
        except FileExistsError:
            print(PATH_EXISTS.format(param))
            failed = True

    ctx.error_level = failed
    ctx.piped = False


def _get_listdir_lines(folder: str, ctx: Context) -> list:
    # pylint: disable=too-many-locals
    files = listdir()
    files.sort()

    files = [".", ".."] + files

    tmp = []
    count = defaultdict(int)

    old_locale = getlocale(LC_NUMERIC)
    setlocale(LC_NUMERIC, getlocale(LC_CTYPE))
    for file_item in files:
        raw = stat(file_item)
        cdate = datetime.fromtimestamp(raw.st_ctime)
        time = cdate.strftime("%X")
        cdate = cdate.strftime("%x")
        is_dir = isdir(file_item)
        dir_text = ""
        if is_dir:
            dir_text = "<DIR>".ljust(DIR_FORMAT_FOLDER_SYMBOL_LJUST)
        size = raw.st_size

        if is_dir:
            count["total_size"] += size
            size = ""
        else:
            size = "{0:n}".format(size).rjust(DIR_FORMAT_FILE_BYTES_RJUST)

        count["folders" if is_dir else "files"] += 1
        tmp.append(f"{cdate}  {time}    {dir_text}  {size} {file_item}")

    prefix = [
        " Volume in drive <NYI> has no label.",
        " Volume Serial Number is <NYI>",
        "",
        f" Directory of {ctx.cwd}",
        ""
    ]

    free_bytes = statvfs(folder)
    free_bytes_avail = free_bytes.f_frsize * free_bytes.f_bavail
    free_bytes = "{0:n}".format(free_bytes_avail).rjust(
        DIR_FORMAT_FREE_BYTES_RJUST
    )
    file_count = str(count["files"]).rjust(DIR_FORMAT_FILE_COUNT_RJUST)
    folder_count = str(count["folders"]).rjust(DIR_FORMAT_FOLDER_COUNT_RJUST)
    used_bytes = "{0:n}".format(count["total_size"]).rjust(
        DIR_FORMAT_TOTAL_SIZE_RJUST
    )
    suffix = [
        f"{file_count} File(s){used_bytes} bytes",
        f"{folder_count} Dir(s){free_bytes} bytes free",
    ]
    setlocale(LC_NUMERIC, old_locale)
    return prefix + tmp + suffix


@what_func
def list_folder(params: List[Argument], ctx: Context) -> None:
    """
    Batch: DIR command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance

    Raises:
        NotImplementedError: when dir command is supplied anything but /?
    """
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

    if params_len == 1 and params[0].lower() == "/?":
        print_help(cmd=CommandType.DIR)
        return
    raise NotImplementedError()


@what_func
def remove_folder(params: List[Argument], ctx: Context) -> None:
    """
    Batch: RMDIR command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    # pylint: disable=too-many-branches
    log = ctx.log.debug

    params = [
        percent_expansion(line=param.value, ctx=ctx)
        for param in params
    ]
    params_len = len(params)

    if not params_len:
        print(SYNTAX_INCORRECT)
        ctx.error_level = 0
        return

    is_help = False
    ignore_files = False
    quiet = False
    out = []
    while params:
        current_param = params.pop(0)
        item_low = current_param.lower()
        if current_param == "/?":
            is_help = True
        elif item_low == "/s":
            ignore_files = True
        elif item_low == "/q":
            quiet = True
        else:
            out.append(current_param)

    if is_help:
        print_help(cmd=CommandType.RMDIR)
        return

    for param in out:
        if not isdir(param):
            log("got %r, is not dir", param)
            print(DIR_INVALID)
            continue
        if listdir(param):
            if not ignore_files:
                print(DIR_NONEMPTY)
                continue
            text = f"{param}, {SURE}"
            if ctx.piped:
                answer = ctx.output.stdout.read(1)
                print(f"{text} {answer}")
            else:
                answer = "y" if quiet else input(f"{text} ").lower()
            if answer != "y":
                continue
        rmtree(param)


@what_func
def rem_comment(params: List[Argument], ctx: Context) -> None:
    """
    Batch: REM command.

    Must NOT modify errorlevel.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    params_len = len(params)
    if not params_len:
        return

    params = [param.value for param in params]
    if params_len == 1 and params[0] == "/?":
        print_help(cmd=CommandType.REM)


def get_cmd_map():
    """
    Get mapping of CommandType into its functions for execution.

    Returns:
        dict with mapping Command enum to a function it should call
    """
    return {
        CommandType.ECHO: echo,
        CommandType.CD: cd,
        CommandType.SET: set_cmd,
        CommandType.PROMPT: prompt,
        CommandType.TITLE: title,
        CommandType.PAUSE: pause,
        CommandType.EXIT: exit_cmd,
        CommandType.SETLOCAL: setlocal,
        CommandType.DELETE: delete,
        CommandType.ERASE: delete,
        CommandType.HELP: help_cmd,
        CommandType.MKDIR: create_folder,
        CommandType.MD: create_folder,
        CommandType.DIR: list_folder,
        CommandType.CLS: clear_screen,
        CommandType.DATE: date,
        CommandType.RMDIR: remove_folder,
        CommandType.RD: remove_folder,
        CommandType.TYPE: type_cmd,
        CommandType.PATH: path_cmd,
        CommandType.REM: rem_comment,
        CommandType.PUSHD: pushd,
        CommandType.POPD: popd
    }


def get_reverse_cmd_map():
    """
    Get reverse mapping for CommandType.

    Returns:
        dictionary with CommandType name: CommantType instance pairs
    """
    rev_cmd_map = {}
    for attr_name in dir(CommandType):
        resolved = getattr(CommandType, attr_name)
        if not isinstance(resolved, CommandType):
            continue
        if attr_name == CommandType.UNKNOWN.name:
            continue
        rev_cmd_map[resolved.value] = resolved
    return rev_cmd_map


def parse(cmd_and_args: str) -> Tuple[CommandType, list]:  # noqa: WPS210
    """
    Parse a string into a command.

    Args:
        cmd_and_args (str): isolated cmd string, e.g. "echo Hello, World"

    Returns:
        tuple with Command and its params in a list
    """
    cmd, *cmd_params = cmd_and_args.split(" ")
    unk = CommandType.UNKNOWN

    cmds = {}
    for attr_name in dir(CommandType):
        resolved = getattr(CommandType, attr_name)
        if attr_name == unk.name:
            continue
        if not isinstance(resolved, CommandType):
            continue
        cmds[resolved.value] = resolved

    found = cmds.get(cmd, unk)
    if found == unk:
        cmd_params = [cmd]
    return (found, cmd_params)
