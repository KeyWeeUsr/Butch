"""
Module that takes already parsed & tokenized Batch input and executes according
to the provided tokens and context.
"""

from typing import Union
from tokenizer import Command, Connector, Pipe, Redirection
from commands import Command as CommandType, get_cmd_map
from context import Context


class UnknownCommand(Exception):
    "Exception if CommandType.UNKNOWN was passed."


def call(cmd: CommandType, params: list, ctx: Context) -> None:
    "Execute the underlying function based on CommandType enum. (deprecated)"
    cmd_map = get_cmd_map()
    func = cmd_map.get(cmd)
    if not func:
        raise UnknownCommand(f"Unknown function: '{cmd}'")

    ctx.history = [cmd, params]
    func(params=params, ctx=ctx)


def new_call(
        cmd: Union[Command, Connector], ctx: Context, child: bool = False
) -> None:
    "Open a Command or Connector object and execute the underlying function."
    log = ctx.log.debug
    log("Calling command %r", cmd)

    obj = cmd
    if isinstance(obj, Connector):
        log("\t- unpacking connector")
        if isinstance(obj, (Pipe, Redirection)):
            log("\t\t- should collect STDOUT+STDERR")
            ctx.collect_output = True
        left = obj.left
        log("\t- recursion to connector's left: %r", left)
        new_call(cmd=left, ctx=ctx, child=True)
        ctx.collect_output = False
        ctx.piped = isinstance(obj, Pipe)
        if isinstance(obj, Redirection):
            log("\t- should write collected output to: %r", None)
            # read ctx.output.stdout/stderr
            # and write to whatever provided as cmd.right
            log("\t\t- not yet implemented")
        obj = obj.right

    cmd_map = get_cmd_map()
    log("\t- function lookup by: %r", obj.cmd)
    func = cmd_map.get(obj.cmd)
    if not func:
        raise UnknownCommand(f"Unknown function: '{cmd}'")

    if not child:
        ctx.history = cmd
    new_cmds = (
        CommandType.SET, CommandType.ECHO,
        CommandType.DELETE, CommandType.ERASE
    )
    if obj.cmd not in new_cmds:
        values = []
        for item in obj.args:
            if item.quoted:
                values.append(repr(item.value))
            else:
                values.append(item.value)
        func(params=values, ctx=ctx)
        return
    func(params=obj.args, ctx=ctx)
