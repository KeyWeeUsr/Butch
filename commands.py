from enum import Enum


class Command(Enum):
    UNKNOWN = "<unknown>"
    ECHO = "echo"


def echo(params: list) -> None:
    print(*params)


CMD_MAP = {
    Command.ECHO: echo
}
