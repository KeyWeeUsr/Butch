from .commands import Command


def parse(values: str):
    cmd, params = values.split(" ")

    if cmd == Command.ECHO:
        return (Command.ECHO, params)
    return (Command.UNKNOWN, cmd)
