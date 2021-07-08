import re
from typing import Tuple
from commands import Command
from context import Context


def parse(values: str) -> Tuple[Command, list]:
    cmd, *params = values.split(" ")
    unk = Command.UNKNOWN.name

    cmds = {
        getattr(Command, item).value: getattr(Command, item)
        for item in dir(Command)
        if isinstance(getattr(Command, item), Command) and item != unk
    }
    print(cmds)

    if cmd in cmds:
        return (cmds[cmd], params)
    return (Command.UNKNOWN, [cmd])


def clear_input(value: str) -> str:
    if set(value) in (set(""), set("\n"), set("\r\n"), set("\n\r")):
        return ""
    return value


def parse_variables(values: str, ctx: Context):
    out = []

    for value in values:
        new = None

        delayed = re.findall(r"!(.*)!", value)
        if delayed:
            delayed = delayed[0]
            new = ctx.get_variable(delayed)
            if new:
                out.append(new)
                continue

        normal = re.findall(r"%(.*)%", value)
        if normal:
            normal = normal[0]
            new = ctx.get_variable(normal)
            if new:
                out.append(new)
                continue
        out.append(value)
    return out
