"""
Module for issuing calls to commands from a tokenized input.

The call function takes the already parsed and tokenized Batch input (by
tokenizer module) and executes according to the provided tokens and context.
"""

from typing import Union

from butch.commands import get_cmd_map
from butch.context import Context
from butch.tokenizer import Command, Connector, Pipe, Redirection


FILE_CHUNK = 512


class UnknownCommand(Exception):
    """Exception if CommandType.UNKNOWN was passed."""


def _handle_redirection(redir_target, ctx: Context):
    log = ctx.log.debug
    log("\t- redirect collected output to: %r", redir_target)

    # read ctx.output.stdout/stderr
    # and write to whatever provided as cmd.right
    path = redir_target.value.replace("\\", "/")
    log("\t\t- writing collected stdout to %r", path)

    out = ctx.output.stdout
    out.seek(0)

    with open(path, "w") as output_descr:
        while True:
            chunk = out.read(FILE_CHUNK)
            if not chunk:
                break
            output_descr.write(chunk)


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
        if isinstance(command, (Pipe, Redirection)):
            log("\t\t- should collect STDOUT+STDERR")
            ctx.collect_output = True
        left = command.left
        log("\t- recursion to connector's left: %r", left)
        new_call(cmd=left, ctx=ctx, child=True)
        ctx.collect_output = False
        ctx.piped = isinstance(command, Pipe)

        if isinstance(command, Redirection):
            _handle_redirection(redir_target=command.right, ctx=ctx)
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
