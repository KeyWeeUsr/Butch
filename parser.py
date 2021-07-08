from typing import Tuple
from commands import Command


def parse(values: str) -> Tuple[Command, list]:
    cmd, *params = values.split(" ")

    if cmd == Command.ECHO.value:
        return (Command.ECHO, params)
    return (Command.UNKNOWN, [cmd])
