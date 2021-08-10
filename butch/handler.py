from os.path import exists

from butch.caller import new_call
from butch.context import Context
from butch.tokenizer import tokenize


def handle_input(inp: str, ctx: Context):
    """
    Handle a Batch input from CLI.

    Args:
        inp: Batch commands as a string
        ctx: Context instance
    """
    for cmd in tokenize(text=inp, ctx=ctx):
        new_call(cmd=cmd, ctx=ctx)


def handle_file(path: str, ctx: Context):
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


def handle(text: str, ctx: Context):
    """
    Handle for file and text.

    Args:
        text: either path or string input
        ctx: Context instance
    """
    if exists(text):
        handle_file(path=text, ctx=ctx)
        return
    handle_input(inp=text, ctx=ctx)
