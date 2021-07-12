import re
from typing import Tuple, List
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

    if cmd in cmds:
        return (cmds[cmd], params)
    return (Command.UNKNOWN, [cmd])


def parse_file(path: str) -> List[Tuple[Command, list]]:
    with open(path) as file:
        lines = file.readlines()
    return [parse(line.rstrip()) for line in lines]


def clear_input(value: str) -> str:
    if set(value) in (set(""), set("\n"), set("\r\n"), set("\n\r")):
        return ""
    return value


def parse_variables(values: list, ctx: Context):
    out = []

    for value in values:
        new = None
        tmp = ""

        delayed = re.findall(r"!(.*?)!", value)
        delay_cont = False
        for item in delayed:
            new = ctx.get_variable(item, delayed=True)
            if new:
                delay_cont = True
                tmp += new
        if delay_cont:
            out.append(tmp)
            tmp = ""
            continue

        normal = re.findall(r"%(.*?)%", value)
        normal_cont = False
        for item in normal:
            new = ctx.get_variable(item)
            if new:
                normal_cont = True
                tmp += new
        if normal_cont:
            out.append(tmp)
            tmp = ""
            continue

        out.append(value)
    return out


def read_line(text: str) -> str:
    return text.replace("\x1a", "\n")


def read_file(path: str) -> list:
    with open(path) as file:
        text = file.read()
    return read_line(text=text).splitlines()
