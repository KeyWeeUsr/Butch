from commands import Command, CMD_MAP
from context import Context


def call(cmd: Command, params: list, ctx: Context):
    func = CMD_MAP.get(cmd)
    if not func:
        raise Exception(f"Unknown function: '{cmd}'")

    func(params, ctx=ctx)
