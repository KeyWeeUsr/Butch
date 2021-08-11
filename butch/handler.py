from os.path import exists
from typing import List

from butch.caller import new_call
from butch.context import Context
from butch.jumptype import JumpTypeEof
from butch.tokenizer import tokenize
from butch.tokens import Label, Token


def collect_labels(cmds: List[Token]):
    return {
        cmd.value: idx
        for idx, cmd in enumerate(cmds)
        if isinstance(cmd, Label)
    }


def handle_input(inp: str, ctx: Context):
    """
    Handle a Batch input from CLI.

    Args:
        inp: Batch commands as a string
        ctx: Context instance
    """
    jump_eof = JumpTypeEof()

    instructions = tokenize(text=inp, ctx=ctx)
    labels = collect_labels(cmds=instructions)

    inst_len = len(instructions)
    inst_ptr = 0
    while 0 <= inst_ptr < inst_len:
        cmd = instructions[inst_ptr]
        new_call(cmd=cmd, ctx=ctx)

        jump = ctx.jump
        if jump == jump_eof:
            break

        if jump and jump.target in labels:
            # the position after the label
            # as the label isn't an executable command
            inst_ptr = labels[jump.target] + 1
            ctx.jump = None
            continue
        inst_ptr += 1


def handle_file(path: str, ctx: Context):
    """
    Open and handle a Batch file.

    Args:
        path: path to the Batch file
        ctx: Context instance
    """
    with open(path) as fdes:
        batch_file = fdes.read()
    handle_input(inp=batch_file, ctx=ctx)


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
