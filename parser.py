from typing import Tuple
from commands import Command


def parse(values: str) -> Tuple[Command, list]:
    cmd, *params = values.split(" ")

    if cmd == Command.ECHO.value:
        return (Command.ECHO, params)
    return (Command.UNKNOWN, [cmd])


def clear_input(value: str) -> str:
    if set(value) in (set(""), set("\n"), set("\r\n"), set("\n\r")):
        return ""
    return value
