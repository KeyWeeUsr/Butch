"""Main module."""

import sys

from argparse import ArgumentParser, Namespace
from os.path import exists

from butch.caller import new_call
from butch.context import Context, get_context
from butch.tokenizer import tokenize


def handle_input_new(inp: str, ctx: Context):
    """
    Handle a Batch input from CLI.

    Args:
        inp: Batch commands as a string
        ctx: Context instance
    """
    for cmd in tokenize(text=inp, ctx=ctx):
        new_call(cmd=cmd, ctx=ctx)


def handle_file_new(path: str, ctx: Context):
    """
    Open and handle a Batch file.

    Args:
        path: path to the Batch file
        ctx: Context instance
    """
    with open(path) as fdes:
        batch_file = fdes.read()
    cmds = tokenize(text=batch_file, ctx=ctx)
    for cmd in cmds:
        new_call(cmd=cmd, ctx=ctx)


def loop(ctx: Context):
    """
    Run the main REPL loop for Batch lang.

    Args:
        ctx: Context instance
    """
    while True:  # noqa: WPS457
        prompt = ""
        if ctx.echo:
            prompt = ctx.resolve_prompt()
        inp = input(prompt)
        handle_input_new(inp=inp, ctx=ctx)


def ctrlc_handler(*_):  # noqa: DAR101
    """
    Handle KeyboardInterrupt/^C exception.

    # noqa: DAR101
    """


def get_cli_parser() -> Namespace:  # noqa: WPS213
    """
    Assemble and return Butch's CLI argument parser.

    Returns:
        argparse.Namespace
    """
    bool_action = "store_true"
    cli = ArgumentParser(prefix_chars="/", prog="butch")
    cli.add_argument("/C", help="Run Command and then terminate", nargs="+")
    cli.add_argument(
        "/K", help="Run Command and then return to the prompt.", nargs="+"
    )

    # :color
    cli.add_argument("/T", help="Sets the foreground/background colours.")

    cli.add_argument("/A", help="Output ANSI characters.")
    cli.add_argument("/U", help="Output UNICODE characters (UCS-2 le).")
    cli.add_argument(
        "/D",
        help=(
            "Ignore registry AutoRun commands.\n"
            r"HKLM | HKCU \Software\Microsoft\Command Processor\AutoRun"
        )
    )

    cli.add_argument(
        "/E:ON",
        help="Enable CMD Command Extensions (default)",
        action=bool_action,
        default=True
    )
    cli.add_argument(
        "/E:OFF",
        help="Disable CMD Command Extensions.",
        action=bool_action
    )

    cli.add_argument(
        "/X", help=(
            "Enable CMD Command Extensions (old switch for compatibility)"
        ),
        default=True
    )
    cli.add_argument(
        "/Y", help=(
            "Disable CMD Command Extensions (old switch for compatibility)"
        )
    )
    cli.add_argument("/Q", help="Turn echo off.", action=bool_action)
    cli.add_argument(
        "/S", help=(
            'Strip " quote characters from command.\n'
            "If command starts with a quote, the first and last quote chars"
            " in command will be removed, whether /s is specified or not."
        )
    )
    cli.add_argument(
        "/V:ON",
        help="Enable delayed environment variable expansion.",
        action=bool_action
    )
    cli.add_argument(
        "/V:OFF",
        help="Diable delayed environment expansion.",
        action=bool_action
    )
    return cli


def mainloop(ctx: Context):
    """
    Run the main loop for Butch handling text, ^C and ^D inputs.

    Args:
        ctx: Context instance
    """
    while True:
        try:
            loop(ctx=ctx)
        except KeyboardInterrupt:
            if not ctrlc_handler():
                print("")
                continue
        except EOFError:
            sys.exit(0)


def handle_new(text: str, ctx: Context):
    """
    Handle for file and text.

    Args:
        text: either path or string input
        ctx: Context instance
    """
    if exists(text):
        handle_file_new(path=text, ctx=ctx)
        return
    handle_input_new(inp=text, ctx=ctx)


def main():
    """Entrypoint function for Butch program."""
    cli = get_cli_parser()
    args = cli.parse_args()
    ctx = get_context()

    ext_off = getattr(args, "E:OFF", None)
    ext_on = getattr(args, "E:ON", None)
    ctx.extensions_enabled = (
        (not ext_off and not args.Y) and (ext_on and args.X)
    )
    ctx.echo = not args.Q

    if args.C:
        handle_new(text=" ".join(args.C), ctx=ctx)
        sys.exit(ctx.error_level)
        return

    if args.K:
        handle_new(text=" ".join(args.K), ctx=ctx)
        mainloop(ctx=ctx)
        return

    mainloop(ctx=ctx)


if __name__ == "__main__":
    main()
