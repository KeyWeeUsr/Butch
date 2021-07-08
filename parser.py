from typing import Tuple
from commands import Command


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
