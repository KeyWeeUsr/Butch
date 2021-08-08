"""Module holding command-representing functions for their Batch names."""

import sys
import ctypes

from collections import defaultdict
from datetime import datetime
from locale import LC_CTYPE, LC_NUMERIC, getlocale, setlocale
from os import environ, getcwd, listdir, makedirs, remove, stat, statvfs
from os.path import abspath, exists, isdir, join
from platform import system
from shutil import rmtree
from typing import List, Tuple

from butch.commandtype import CommandType
from butch.constants import (
    ACCESS_DENIED, DELETE, DIR_INVALID, DIR_NONEMPTY, ENV_VAR_UNDEFINED,
    ERROR_PROCESSING, FILE_NOT_FOUND, PARAM_HELP, PARAM_YES, PATH_EXISTS,
    PATH_NOT_FOUND, PAUSE_TEXT, SURE, SYNTAX_INCORRECT, ECHO_STATE, OCTAL_CLEAR
)
from butch.context import Context
from butch.expansion import percent_expansion
from butch.help import print_help
from butch.outputs import CommandOutput
from butch.tokens import Argument


DIR_FORMAT_TOTAL_SIZE_RJUST = 14
DIR_FORMAT_FILE_COUNT_RJUST = 17
DIR_FORMAT_FOLDER_COUNT_RJUST = 18
DIR_FORMAT_FREE_BYTES_RJUST = 14
DIR_FORMAT_FOLDER_SYMBOL_LJUST = 14
DIR_FORMAT_FILE_BYTES_RJUST = 14
LOG_STR = "<cmd: %-8.8s>, params: %r, ctx: %r"


def what_func(func):
    """
    Command logging decorator.

    Args:
        func (Callable): function to wrap in the decorator

    Returns:
        function wrapper
    """
    def wrapper(*args, **kwargs):
        ctx = kwargs.get("ctx")
        params = kwargs.get("params")
        if ctx:
            ctx.log.debug(LOG_STR, func.__name__, params, ctx)
        return func(*args, **kwargs)
    return wrapper


def _expand_params(params: List[Argument], ctx: Context):
    return [percent_expansion(line=param.value, ctx=ctx) for param in params]


def get_output(ctx: Context):
    """
    Get STDOUT buffer according to the Context settings.

    Args:
        ctx (Context): Context instance
    """
    out = sys.stdout
    log = ctx.log.debug
    if ctx.collect_output:
        log("\t- should collect output")
        if not ctx.output:
            log("\t\t- using existing output instance")
            ctx.output = CommandOutput()
        out = ctx.output.stdout
    return out


def get_error(ctx: Context):
    """
    Get STDERR buffer according to the Context settings.

    Args:
        ctx (Context): Context instance
    """
    err = sys.stderr
    log = ctx.log.debug
    if ctx.collect_output:
        log("\t- should collect error")
        if not ctx.output:
            log("\t\t- using existing output instance")
            ctx.output = CommandOutput()
        err = ctx.output.stderr
    return err


@what_func
def echo(params: List[Argument], ctx: Context) -> None:
    """
    Batch: ECHO command.

    Must NOT set error level to 0.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    out = get_output(ctx=ctx)

    params = _expand_params(params=params, ctx=ctx)
    params_len = len(params)
    state_map = {True: "on", False: "off"}
    state_rev = {state: key for key, state in state_map.items()}

    if params_len == 1:
        first = params[0].lower()
        if first in ("on", "off"):
            ctx.echo = state_rev[first]
            return
        if first == PARAM_HELP:
            print_help(cmd=CommandType.ECHO, file=out)
            return

    if not params_len:
        echo_state = state_map[ctx.echo]
        print(ECHO_STATE.format(echo_state), file=out)
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
    out = get_output(ctx=ctx)

    params = _expand_params(params=params, ctx=ctx)
    params_len = len(params)

    if not params_len:
        print(SYNTAX_INCORRECT, file=out)
        ctx.error_level = 1
        return

    if params_len == 1:
        first = params[0]
        if first == PARAM_HELP:
            print_help(cmd=CommandType.TYPE, file=out)
            return

        if isdir(first):
            print(ACCESS_DENIED, file=out)
            ctx.error_level = 1
            return

        if not exists(first):
            print(FILE_NOT_FOUND, file=out)
            ctx.error_level = 1
            return

        _type_file(path=first, output=out)
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

        _type_file(path=item_path, output=out)
        # no trailing newline after files
        if idx != params_len - 1:
            print("\n", file=out)


def _type_file(path: str, output):
    with open(path) as file_desc:
        # TODO: big files chunking
        print(file_desc.read(), file=output)


@what_func
def path_cmd(params: List[Argument], ctx: Context) -> None:
    """
    Batch: PATH command.

    Must NOT set errorlevel.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    out = get_output(ctx=ctx)

    params = _expand_params(params=params, ctx=ctx)
    params_len = len(params)

    if not params_len:
        path = ctx.get_variable("PATH") or "(null)"
        print(f"PATH={path}", file=out)
        return

    first = params[0].lower()
    if first == PARAM_HELP:
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

    Must NOT set error_level on empty param list.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    out = get_output(ctx=ctx)

    params = _expand_params(params=params, ctx=ctx)
    params_len = len(params)

    if not params_len:
        print(file=out)
        return

    first = params[0].lower()
    if first == PARAM_HELP:
        print_help(cmd=CommandType.PUSHD, file=out)
        return

    path = " ".join(params)
    try:
        ctx.push_folder(path=path)
    except FileNotFoundError:
        ctx.error_level = 1
        print(PATH_NOT_FOUND, file=sys.stderr)


@what_func
def popd(params: List[Argument], ctx: Context) -> None:
    """
    Batch: POPD command.

    Must NOT set errorlevel.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    log = ctx.log.debug
    out = get_output(ctx=ctx)

    params = _expand_params(params=params, ctx=ctx)

    first = params[0].lower() if params else ""
    if first == PARAM_HELP:
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
    out = get_output(ctx=ctx)

    cmd_map = get_reverse_cmd_map()
    params = _expand_params(params=params, ctx=ctx)
    if not params:
        print_help(cmd=CommandType.HELP, file=out)
        return

    print_help(
        cmd=cmd_map.get(params[0].lower(), CommandType.UNKNOWN), file=out
    )


def _print_all_variables(ctx: Context, file=sys.stdout) -> None:
    for key, found_value in ctx.variables.items():
        print(f"{key}={found_value}", file=file)


def _print_single_variable(key: str, ctx: Context, file=sys.stdout) -> None:
    found_value = ctx.get_variable(key=key)
    if not found_value:
        print(ENV_VAR_UNDEFINED, file=file)
        return
    print(f"{key}={found_value}", file=file)


@what_func
def set_cmd(params: List[Argument], ctx: Context) -> None:
    """
    Batch: SET command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    ctx.error_level = 0
    log = ctx.log.debug
    out = get_output(ctx=ctx)

    should_prompt = False

    params_len = len(params)
    if not params_len:
        _print_all_variables(ctx=ctx, file=out)
        return

    param = params[0]
    quoted = param.quoted
    param_value = param.value
    if params_len == 1 and param_value == PARAM_HELP:
        print_help(cmd=CommandType.SET, file=out)
        return

    if params_len >= 2 and param_value.lower() == "/p":
        should_prompt = True
        param_value = " ".join(param.value for param in params[1:])

    # >1 values are ignored
    if quoted:
        log("\t- quoted variable")
        param_value = param_value[1:param_value.rfind('"')]

    eq_sign = "="
    if eq_sign not in param_value and not should_prompt:
        log("\t- single variable print: %r", param_value)
        _print_single_variable(key=param_value, ctx=ctx, file=out)
        return

    left, right = param_value.split(eq_sign)
    if left and not right:
        if should_prompt:
            log("\t- single variable prompt: %r", left)
            if ctx.inputted:
                value_to_set = ctx.input.stdin.readline().rstrip("\n")
            else:
                value_to_set = input()
            if not value_to_set:
                ctx.error_level = 1
                return
            ctx.set_variable(key=left, value_to_set=value_to_set)
        else:
            log("\t- single variable delete: %r", left)
            ctx.delete_variable(key=left.lower())
        return

    left = left.lower()
    log("\t- single variable create: %r, %r", left, right)
    if should_prompt:
        log("\t- single variable prompt: %r", left)
        if ctx.inputted:
            print(right, file=out)
            value_to_set = ctx.input.stdin.readline().rstrip("\n")
            log("\t- read from STDIN: %r", value_to_set)
        else:
            value_to_set = input(right)
        if not value_to_set:
            ctx.error_level = 1
            return
        ctx.set_variable(key=left, value_to_set=value_to_set)
    else:
        ctx.set_variable(key=left, value_to_set=right)


@what_func
def setlocal(params: list, ctx: Context) -> None:
    """
    Batch: SETLOCAL command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """

    out = get_output(ctx=ctx)

    params_len = len(params)
    if not params_len:
        # TODO: copy all variables to new session
        # TODO: restore old state with endlocal
        raise NotImplementedError("SETLOCAL")

    params = _expand_params(params=params, ctx=ctx)
    if params_len == 1 and params[0] == PARAM_HELP:
        print_help(cmd=CommandType.SETLOCAL, file=out)
        return

    # TODO: add bat-test, it's probably broken now
    first = [param.lower() for param in set(params)][0]
    if first == "enabledelayedexpansion":
        ctx.delayed_expansion_enabled = True
    elif first == "disabledelayedexpansion":
        ctx.delayed_expansion_enabled = False
    elif first == "enableextensions":
        ctx.extensions_enabled = True
    elif first == "disableextensions":
        ctx.extensions_enabled = False


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

    out = get_output(ctx=ctx)

    params_len = len(params)
    if not params:
        # linux
        ctx.cwd = environ.get("HOME")
        # windows
        return

    params = _expand_params(params=params, ctx=ctx)
    first = params[0]
    if params_len == 1 and first == PARAM_HELP:
        print_help(cmd=CommandType.CD, file=out)
        return

    try:
        ctx.cwd = first
    except FileNotFoundError:
        ctx.error_level = 1
        print(PATH_NOT_FOUND, file=sys.stderr)


@what_func
def prompt(params: list, ctx: Context) -> None:
    """
    Batch: PROMPT command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    ctx.error_level = 0

    out = get_output(ctx=ctx)

    params_len = len(params)
    if not params_len:
        ctx.error_level = 1
        print(file=out)
        return

    params = _expand_params(params=params, ctx=ctx)
    first = params[0]
    if params_len == 1 and first == PARAM_HELP:
        print_help(cmd=CommandType.PROMPT, file=out)
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

    Raises:
        WinError: raised when console title can't be set via Win32 API
    """
    ctx.error_level = 0

    out = get_output(ctx=ctx)

    params_len = len(params)
    if not params_len:
        print(file=out)
        return

    first = params[0]
    if params_len == 1 and first == PARAM_HELP:
        print_help(cmd=CommandType.TITLE, file=out)
        return

    platform_name = system()
    if platform_name == "Linux":
        text = params[0]
        sys.stdout.write(f"\x1b]2;{text}\x07")
    elif platform_name == "Windows":
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
    out = get_output(ctx=ctx)

    first = params[0].value if params else ""
    if first == PARAM_HELP:
        print_help(cmd=CommandType.DATE, file=out)
        return

    now = datetime.now()
    if first.upper() == "/T":
        # should match the locale format
        print(now.strftime("%x"), file=out)
        return

    now = now.strftime("%a %x")
    print(f"The current date is: {now}", file=out)
    print("Enter the new date: (mm-dd-yy)", file=out)
    print("Setting the date is not implemented, use /T", file=sys.stderr)
    try:
        input()
    except KeyboardInterrupt:
        ctx.error_level = 1


@what_func
def time(params: list, ctx: Context) -> None:
    """
    Batch: TIME command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    ctx.error_level = 0
    out = get_output(ctx=ctx)

    first = params[0].value if params else ""
    if first == PARAM_HELP:
        print_help(cmd=CommandType.TIME, file=out)
        return

    now = datetime.now()
    now = now.strftime("%X")
    if first.upper() == "/T":
        # should match the locale format
        print(now, file=out)
        return

    print(f"The current time is: {now}", file=out)
    print("Enter the new time: ", file=out)
    print("Setting the date is not implemented, use /T", file=sys.stderr)
    try:
        input()
    except KeyboardInterrupt:
        ctx.error_level = 1


@what_func
def pause(params: list, ctx: Context) -> None:
    """
    Batch: PAUSE command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    ctx.error_level = 0
    out = get_output(ctx=ctx)

    params = _expand_params(params=params, ctx=ctx)
    first = params[0] if params else ""
    if first == PARAM_HELP:
        print_help(cmd=CommandType.PAUSE, file=out)
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
    out = get_output(ctx=ctx)
    params = _expand_params(params=params, ctx=ctx)

    first = params[0] if params else ""
    if first == PARAM_HELP:
        print_help(cmd=CommandType.CLS, file=out)
        return
    print(OCTAL_CLEAR if "DEBUG" not in environ else "<clear>", file=out)


@what_func
def exit_cmd(params: list, ctx: Context) -> None:
    """
    Batch: EXIT command.

    Args:
        params (list): list of Argument instances for the Command
        ctx (Context): Context instance
    """
    ctx.error_level = 0
    out = get_output(ctx=ctx)
    params = _expand_params(params=params, ctx=ctx)

    if not params:
        sys.exit(0)
        return

    first = params[0]
    if first == PARAM_HELP:
        print_help(cmd=CommandType.EXIT, file=out)
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

    out = get_output(ctx=ctx)
    params = _expand_params(params=params, ctx=ctx)
    params_len = len(params)

    if not params_len:
        print(SYNTAX_INCORRECT, file=out)
        ctx.error_level = 1
        return

    if params_len == 1:
        first = params[0]
        if first.lower() == PARAM_HELP:
            print_help(cmd=CommandType.DELETE, file=out)
            return
        file_path = abspath(first)
        if not exists(file_path):
            os_path = file_path.replace("/", "\\")
            print(f"Could Not Find {os_path}", file=sys.stderr)
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
    for param in params:  # noqa: WPS440
        path = abspath(param)
        if not exists(path):
            continue

        os_path = path.replace("/", "\\")
        if isdir(param):
            answer = ""
            if prompt_for_all or not quiet:
                text = rf"{os_path}\*, {SURE}"
                if ctx.piped:
                    answer = ctx.output.stdout.read(1)
                    print(f"{text} {answer}", file=out)
                else:
                    answer = input(f"{text} ", file=out).lower()
            if answer != PARAM_YES:
                continue
            for file_item in listdir(param):
                remove(join(path, file_item))
            return
        if prompt_for_all:
            answer = ""
            text = f"{os_path}, {DELETE}"
            if ctx.piped:
                answer = ctx.output.stdout.read(1)
                print(f"{text} {answer}", file=out)
            else:
                answer = input(text, file=out).lower()
            if answer != PARAM_YES:
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
    out = get_output(ctx=ctx)
    params = _expand_params(params=params, ctx=ctx)
    params_len = len(params)

    if not params_len:
        # do this also for piped input as mkdir does not care about pipes
        # echo hello | mkdir -> syntax incorrect
        print(SYNTAX_INCORRECT, file=sys.stderr)
        ctx.error_level = 1
        return

    if params_len == 1:
        first = params[0]
        if first.lower() == PARAM_HELP:
            print_help(cmd=CommandType.MKDIR, file=out)
            return
        first = first.replace("\\", "/")
        dir_path = abspath(first)
        try:
            makedirs(dir_path)
        except FileExistsError:
            print(PATH_EXISTS.format(first), file=sys.stderr)
            ctx.error_level = 1
        return

    failed = False
    for param in params:
        try:
            makedirs(param)
        except FileExistsError:
            print(PATH_EXISTS.format(param), file=sys.stderr)
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
        file_time = cdate.strftime("%X")
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
        tmp.append(f"{cdate}  {file_time}    {dir_text}  {size} {file_item}")

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
    out = get_output(ctx=ctx)
    params = _expand_params(params=params, ctx=ctx)
    params_len = len(params)

    if not params_len:
        # show current directory list
        lines = _get_listdir_lines(folder=getcwd(), ctx=ctx)
        print("\n".join(lines), file=out)
        ctx.error_level = 0
        return

    if params_len == 1 and params[0].lower() == PARAM_HELP:
        print_help(cmd=CommandType.DIR, file=out)
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

    params = _expand_params(params=params, ctx=ctx)
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
        if current_param == PARAM_HELP:
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
                answer = PARAM_YES if quiet else input(f"{text} ").lower()
            if answer != PARAM_YES:
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
    out = get_output(ctx=ctx)
    params_len = len(params)
    if not params_len:
        return

    params = [param.value for param in params]
    if params_len == 1 and params[0] == PARAM_HELP:
        print_help(cmd=CommandType.REM, file=out)


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
        CommandType.POPD: popd,
        CommandType.TIME: time
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
