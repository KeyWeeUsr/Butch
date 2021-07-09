from commands import Command, get_cmd_map
from context import Context


def call(cmd: Command, params: list, ctx: Context):
    cmd_map = get_cmd_map()
    func = cmd_map.get(cmd)
    if not func:
        raise Exception(f"Unknown function: '{cmd}'")

    ctx.history = [cmd, params]
    func(params=params, ctx=ctx)
