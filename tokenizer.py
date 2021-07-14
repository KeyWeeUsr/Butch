from collections import defaultdict
from enum import Enum, auto
from context import Context
from commands import Command as CommandType, get_reverse_cmd_map

# consecutive delims should be treated as one
# no delims within a quoted string
DELIM_SPACE = " "
DELIM_TAB = "\t"
DELIM_SEMI = ";"
DELIM_COMMA = ","
DELIM_EQ = "="
DELIM_VERTAB = "\x0B"
DELIM_FORMFEED = "\x0C"
DELIM_WTF = "\xff"
DELIM_WHITE = [DELIM_SPACE, DELIM_TAB]
DELIMS = DELIM_WHITE + [
    DELIM_SEMI,
    DELIM_COMMA,
    DELIM_EQ,
    DELIM_VERTAB,
    DELIM_FORMFEED,
    DELIM_WTF
]

SPECIAL_CR = "\r"
SPECIAL_CARRET = "^"
SPECIAL_LPAREN = "("
SPECIAL_RPAREN = ")"
SPECIAL_AT = "@"
SPECIAL_AMP = "&"
SPECIAL_PIPE = "|"
SPECIAL_LT = "<"
SPECIAL_GT = ">"
SPECIAL_REDIR = [
    SPECIAL_LT,
    SPECIAL_GT
]
SPECIAL_SPLITTERS = [
    SPECIAL_AMP,
    SPECIAL_PIPE
] + SPECIAL_REDIR
SPECIAL_LF = "\n"
SPECIALS = [
    SPECIAL_CR,
    SPECIAL_CARRET,
    SPECIAL_LPAREN,
    SPECIAL_RPAREN,
    SPECIAL_AT,
    SPECIAL_LF
] + SPECIAL_SPLITTERS + DELIMS

QUOTE_DOUBLE = '"'
TOKENS = SPECIALS + [QUOTE_DOUBLE]


class Flag(Enum):
    ESCAPE = auto()
    QUOTE = auto()


class Argument:
    _value: str = ""

    def __init__(self, value: str):
        self._value = value

    @property
    def value(self):
        return self._value


class Command:
    _cmd: CommandType = None
    _name: str = ""
    _value: str = ""
    _echo: bool = True

    def __init__(self, cmd: CommandType, value: str, echo: bool = True):
        self._cmd = cmd
        self._name = cmd.value
        self._value = value
        self._echo = echo

    @property
    def cmd(self):
        return self._cmd

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def echo(self):
        return self._echo

    def __repr__(self):
        prefix = "@" if not self.echo else ""
        return f'<{prefix}Command: "{self.name}" ({self.value})>'


class Connector:
    _name: str = ""
    _left: Command = None
    _right: Command = None

    def __init__(self, name: str, left: Command, right: Command):
        self._name = name
        self._left = left
        self._right = right

    @property
    def name(self):
        return self._name

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    def __repr__(self):
        return f'<{self.name}: [{self.left}, {self.right}]>'


class Concat(Connector):
    def __init__(self, left: Command, right: Command):
        super("Concat", left=left, right=right)


class Pipe(Connector):
    def __init__(self, left: Command, right: Command):
        super("Pipe", left=left, right=right)


class RedirType(Enum):
    INPUT = auto()
    OUTPUT = auto()


class Redirection(Connector):
    _type: RedirType
    _append: bool = False

    def __init__(
            self, redir_type: RedirType,
            left: Command, right: Command,
            append: bool = False
    ):
        super("Redirection", left=left, right=right)
        self._type = redir_type
        self._append = append

    @property
    def type(self):
        return self._type

    @property
    def append(self):
        return self._append

    def __repr__(self):
        direction = "?"
        if self.type == Redir.INPUT:
            direction = "<"
        elif self.type == Redir.OUTPUT:
            direction = ">"
        if self.append:
            direction *= 2
        return f'<{self.name}: {self.left} {direction} {self.right}>'


def _finish_buffer(buff: str, output: list) -> None:
    cmd_map = get_reverse_cmd_map()
    # naive
    cmd_clear = buff.lstrip()
    next_white = cmd_clear.find(" ")  # what if \t?

    echo = True
    if cmd_clear.startswith("@"):
        echo = False
        cmd_clear = cmd_clear[1:]

    cmd_raw = cmd_clear
    cmd_val = cmd_clear
    if next_white > 0:
        cmd_raw = cmd_clear[:next_white]
        cmd_val = cmd_clear[next_white + 1:]
    if cmd_raw:
        cmd = cmd_map.get(cmd_raw, CommandType.UNKNOWN)
        output.append(Command(
            # skip after the first whitespace
            cmd=cmd, value=cmd_val, echo=echo
        ))


def tokenize(text: str, ctx: Context, debug: bool = False) -> list:
    from parser import percent_expansion
    output = []

    idx = 0
    text = "\n".join([
        percent_expansion(line, ctx=ctx)
        for line in text.split("\n")  # splitlines strips the last \n
    ])
    text_len = len(text)
    last_pos = text_len - 1
    flags = defaultdict(bool)
    compound_count = 0

    buff = ""
    while idx < text_len:
        char = text[idx]
        next_char = ""

        # last char isn't <LF>
        if char != SPECIAL_LF and idx == last_pos:
            # append last char because finishing
            # and if buff is empty (single-char), then copy char to buff
            buff += char
            if char == SPECIAL_CARRET:
                flags[Flag.ESCAPE] = True
            elif char == QUOTE_DOUBLE:
                flags[Flag.QUOTE] = not flags[Flag.QUOTE]
            _finish_buffer(buff=buff, output=output)
            break

        if char == SPECIAL_CR:
            idx += 1
        elif char == SPECIAL_CARRET:
            flags[Flag.ESCAPE] = True
            idx += 1
        elif char == QUOTE_DOUBLE:
            flags[Flag.QUOTE] = not flags[Flag.QUOTE]
            idx += 1
            if not flags[Flag.QUOTE]:
                output.append(buff)
                buff = ""
        elif char == SPECIAL_LF:
            # SO says this, but CLI says no
            # if not flags[Flag.ESCAPE]:
            flags[Flag.QUOTE] = False
            if flags[Flag.ESCAPE]:
                # keep escape, move
                pass
            else:
                # reverse me later to "if not" + main
                _finish_buffer(buff=buff, output=output)
            if compound_count > 0:
                # do not move to the next line,
                # join buff to single command
                pass

            
            idx += 1
        elif char in SPECIAL_SPLITTERS:
            left = Command(name="???", value=buff)
            right = ...
            join = None
            if char == SPECIAL_PIPE:
                if next_char == SPECIAL_PIPE:
                    join = Concat(left=left, right=right)
                else:
                    join = Pipe(left=left, right=right)
            elif char == SPECIAL_AMP:
                join = Concat(left=left, right=right)
            elif char in SPECIAL_REDIR:
                join = Redirection(
                    left=left, right=right,
                    append=next_char in SPECIAL_REDIR
                )
        elif char == SPECIAL_LPAREN:
            compound_count += 1
            idx += 1
        elif char == SPECIAL_RPAREN:
            compound_count -= 1
            idx += 1
        else:
            buff += char
            idx += 1

    if debug:
        return list(flags.items())
    return output
