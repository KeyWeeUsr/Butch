"""
Module for issuing calls to commands from a tokenized input.

The call function takes the already parsed and tokenized Batch input (by
tokenizer module) and executes according to the provided tokens and context.
"""

from typing import Union

from butch.commands import get_cmd_map
from butch.context import Context
from butch.inputs import CommandInput
from butch.tokenizer import Command, Connector, Pipe, Redirection, RedirType


FILE_CHUNK = 512


class UnknownCommand(Exception):
    """Exception if CommandType.UNKNOWN was passed."""


def _handle_redirection_output(redir_target: str, ctx: Context):
    log = ctx.log.debug
    log("\t- redirect collected output to: %r", redir_target)

    # read ctx.output.stdout/stderr
    # and write to whatever provided as cmd.right
    path = redir_target.replace("\\", "/")
    log("\t\t- writing collected stdout to %r", path)

    out = ctx.output.stdout
    out.seek(0)

    with open(path, "w") as output_descr:
        while True:
            chunk = out.read(FILE_CHUNK)
            if not chunk:
                break
            output_descr.write(chunk)


def _handle_redirection_input(redir_target: str, ctx: Context):
    log = ctx.log.debug
    log("\t\t- should create STDIN")
    ctx.inputted = True
    ctx.input = CommandInput()
    input_buff = ctx.input.stdin

    path = redir_target.replace("\\", "/")
    log("\t\t\t- creating from %r", path)
    with open(path) as stdin:
        while True:
            chunk = stdin.read(FILE_CHUNK)
            if not chunk:
                break
            input_buff.write(chunk)
    input_buff.seek(0)


def new_call(  # noqa: WPS317
        cmd: Union[Command, Connector],  # noqa: WPS318
        ctx: Context, child: bool = False  # noqa: WPS318
) -> None:
    """
    Open a Command or Connector object and execute the underlying function.

    Args:
        cmd (Union[Command, Connector]): single token to process
        ctx (Context): Context instance
        child (bool): set to True if nesting, used for Connectors

    Raises:
        UnknownCommand: for unknown token (mistake or tokenization error)
    """
    log = ctx.log.debug
    log("Calling command %r", cmd)

    command = cmd
    if isinstance(command, Connector):
        log("\t- unpacking connector")
        is_redir = isinstance(command, Redirection)
        is_pipe = isinstance(command, Pipe)
        is_redir_output = False

        if is_redir and command.type == RedirType.OUTPUT:
            is_redir_output = True

        if is_redir or is_pipe:
            if is_redir_output or is_pipe:
                log("\t\t- should collect STDOUT+STDERR")
                ctx.collect_output = True
            else:
                _handle_redirection_input(
                    redir_target=command.right.value, ctx=ctx
                )
        left = command.left
        log("\t- recursion to connector's left: %r", left)
        new_call(cmd=left, ctx=ctx, child=True)
        ctx.collect_output = False
        ctx.piped = isinstance(command, Pipe)

        if is_redir:
            log("\t- finishing redirection")
            if is_redir_output:
                log("\t\t- writing output")
                _handle_redirection_output(
                    redir_target=command.right.value, ctx=ctx
                )
            log("\t\t- done")
            return
        command = command.right

    cmd_map = get_cmd_map()
    log("\t- function lookup by: %r", command.cmd)
    func = cmd_map.get(command.cmd)
    if not func:
        raise UnknownCommand(f"Unknown function: '{cmd}'")

    if not child:
        ctx.history = cmd
    func(params=command.args, ctx=ctx)
