import re
import sys
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


def percent_expansion(line: str, ctx: Context) -> str:
    tmp = ""
    idx = 0
    line_len = len(line)
    while idx < line_len:
        char = line[idx]
        if char != "%":
            tmp += char
            idx += 1
            continue

        if line_len == 1:
            break

        next_perc = line.find("%", idx + 1)
        # %%
        if idx == next_perc:
            if idx + 1 != line_len:
                tmp += "%"
            idx += 1
            continue

        next_idx = idx + 1
        # sys argv
        # %1hello% -> <argv>hello instead of <1hello value>
        if idx < line_len - 1:
            next_char = line[next_idx]
            if next_char.isdigit():
                pos = int(line[next_idx])
                val = sys.argv[pos:pos + 1]
                # value or position/number
                tmp += val[0] if val else str(pos)
                idx = next_idx + 1
                continue
            elif next_char == "*":
                tmp += " ".join(sys.argv[1:10])
                idx = next_idx + 1
                continue
            elif next_char == "%":
                tmp += next_char
                idx = next_idx + 1
                continue

        if next_perc < 0:
            idx += 1
            continue

        # variable expansion
        idx_ahead = next_perc + 1
        perc_range = next_perc - idx
        if next_perc and perc_range > 1 and " " not in line[idx:idx_ahead]:
            tmp += ctx.get_variable(key=line[next_idx:next_perc])
            idx = idx_ahead
            continue

        # escaped %, as %% -> %
        if next_perc and perc_range == 1:
            tmp += "%"
            idx = idx_ahead
            continue
        if next_perc and not perc_range:
            idx += 1
            if idx != line_len:
                tmp += "%"
            continue
    return tmp
