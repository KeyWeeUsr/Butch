"Main module."

import sys

from argparse import ArgumentParser
from os.path import exists

from parser import parse, clear_input, parse_file
from caller import call, new_call
from context import get_context, Context
from tokenizer import tokenize


def handle_input(inp: str, ctx: Context):
    "Handle a Batch input from CLI. (deprecated)"
    inp = clear_input(inp)
    if not inp:
        return

    cmd, params = parse(inp)
    call(cmd=cmd, params=params, ctx=ctx)


def handle_input_new(inp: str, ctx: Context):
    "Handle a Batch input from CLI."
    for cmd in tokenize(text=inp, ctx=ctx):
        new_call(cmd=cmd, ctx=ctx)


def handle_file(path: str, ctx: Context):
    "Open and handle a Batch file. (deprecated)"
    cmds = parse_file(path)
    for cmd, params in cmds:
        call(cmd=cmd, params=params, ctx=ctx)


def handle_file_new(path: str, ctx: Context):
    "Open and handle a Batch file."
    with open(path) as file:
        content = file.read()
    cmds = tokenize(text=content, ctx=ctx)
    for cmd in cmds:
        new_call(cmd=cmd, ctx=ctx)


def loop(ctx: Context):
    "Main REPL loop for Batch lang."
    while True:
        prompt = ""
        if ctx.echo:
            prompt = ctx.resolve_prompt()
        inp = input(prompt)
        handle_input(inp=inp, ctx=ctx)


def ctrlc_handler(*_):
    "Handler for KeyboardInterrupt/^C exception."
    return False


def get_cli_parser():
    "Assemble and return Butch's CLI argument parser."
    cli = ArgumentParser(prefix_chars="/", prog="butch")
    cli.add_argument("/C", help="Run Command and then terminate", nargs="+")
    cli.add_argument(
        "/K", help="Run Command and then return to the prompt.", nargs="+"
    )

    # :color
    cli.add_argument("/T", help="Sets the foreground/background colours.")

    cli.add_argument("/A", help="Output ANSI characters.")
    cli.add_argument("/U", help="Output UNICODE characters (UCS-2 le).")
    cli.add_argument("/D", help=(
        "Ignore registry AutoRun commands.\n"
        r"HKLM | HKCU \Software\Microsoft\Command Processor\AutoRun"
    ))

    cli.add_argument(
        "/E:ON", help="Enable CMD Command Extensions (default)",
        action="store_true", default=True
    )
    cli.add_argument(
        "/E:OFF", help="Disable CMD Command Extensions.",
        action="store_true"
    )

    cli.add_argument("/X", help=(
        "Enable CMD Command Extensions (old switch for compatibility)"
    ), default=True)
    cli.add_argument("/Y", help=(
        "Disable CMD Command Extensions (old switch for compatibility)"
    ))
    cli.add_argument("/Q", help="Turn echo off.", action="store_true")
    cli.add_argument("/S", help=(
        'Strip " quote characters from command.\n'
        "If command starts with a quote, the first and last quote"
        " chars in command will be removed, whether /s is specified or not."
    ))
    cli.add_argument("/V:ON", help=(
        "Enable delayed environment variable expansion."
    ), action="store_true")
    cli.add_argument("/V:OFF", help=(
        "Diable delayed environment expansion."
    ), action="store_true")
    return cli


def mainloop(ctx: Context):
    "Main loop for Butch handling text, ^C and ^D inputs."
    while True:
        try:
            loop(ctx=ctx)
        except KeyboardInterrupt:
            if not ctrlc_handler():
                print()
                continue
        except EOFError:
            sys.exit(0)


def handle(text: str, ctx: Context):
    "Handle for file and text. (deprecated)"
    if exists(text):
        return handle_file(path=text, ctx=ctx)
    return handle_input(inp=text, ctx=ctx)


def handle_new(text: str, ctx: Context):
    "Handle for file and text."
    if exists(text):
        return handle_file_new(path=text, ctx=ctx)
    return handle_input_new(inp=text, ctx=ctx)


def main():
    "Entrypoint function for Butch program."
    cli = get_cli_parser()
    args = cli.parse_args()
    ctx = get_context()

    ctx.extensions_enabled = (
        (not getattr(args, "E:OFF", None) and not args.Y)
        and (getattr(args, "E:ON", None) and args.X)
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
