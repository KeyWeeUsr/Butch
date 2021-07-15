from typing import Union
from tokenizer import Command, Connector
from commands import Command as CommandType, get_cmd_map
from context import Context


def call(cmd: CommandType, params: list, ctx: Context) -> None:
    cmd_map = get_cmd_map()
    func = cmd_map.get(cmd)
    if not func:
        raise Exception(f"Unknown function: '{cmd}'")

    ctx.history = [cmd, params]
    func(params=params, ctx=ctx)


def new_call(cmd: Union[Command, Connector], ctx: Context) -> None:
    ctx.log.debug("Calling command %r", cmd)
    if isinstance(cmd, Connector):
        raise NotImplementedError("connectors")
    cmd_map = get_cmd_map()
    func = cmd_map.get(cmd.cmd)
    if not func:
        raise Exception(f"Unknown function: '{cmd}'")

    ctx.history = [cmd]
    if cmd.cmd in (CommandType.SET, CommandType.ECHO):
        func(params=cmd.args, ctx=ctx)
        return

    values = []
    for item in cmd.args:
        if item.quoted:
            values.append(repr(item.value))
        else:
            values.append(item.value)
    func(params=values, ctx=ctx)
