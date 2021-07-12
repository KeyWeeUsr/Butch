from collections import defaultdict
from enum import Enum, auto

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
DELIMS = [
    DELIM_SPACE,
    DELIM_TAB,
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
SPECIAL_AT = "@"
SPECIAL_AMP = "&"
SPECIAL_PIPE = "|"
SPECIAL_LT = "<"
SPECIAL_GT = ">"
SPECIAL_LF = "\n"
SPECIALS = [
    SPECIAL_CR,
    SPECIAL_CARRET,
    SPECIAL_LPAREN,
    SPECIAL_AT,
    SPECIAL_AMP,
    SPECIAL_PIPE,
    SPECIAL_LT,
    SPECIAL_GT,
    SPECIAL_LF
] + DELIMS

QUOTE_DOUBLE = '"'
TOKENS = SPECIALS + [QUOTE_DOUBLE]


class Flag(Enum):
    ESCAPE = auto()
    QUOTE = auto()


class Command:
    _name: str = ""
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return f'<Command: "{self.name}">'


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

    def __init__(self, redir_type: RedirType, left: Command, right: Command):
        super("Redirection", left=left, right=right)
        self._type = redir_type

    @property
    def type(self):
        return self._type

    def __repr__(self):
        direction = "?"
        if self.type == Redir.INPUT:
            direction = "<-"
        elif self.type == Redir.OUTPUT:
            direction = "->"
        return f'<{self.name}: {self.left} {direction} {self.right}>'


def tokenize(text: str, debug: bool = False) -> list:
    output = []

    idx = 0
    text_len = len(text)
    flags = defaultdict(bool)

    buff = ""
    while idx < text_len:
        char = text[idx]
        if char == SPECIAL_CR:
            idx += 1
            continue
        elif char == SPECIAL_CARRET:
            flags[Flag.ESCAPE] = True
            idx += 1
            continue
        elif char == QUOTE_DOUBLE:
            flags[Flag.QUOTE] = not flags[Flag.QUOTE]
            idx += 1
            if not flags[Flag.QUOTE]:
                output.append(buff)
                buff = ""
            continue
        elif char == SPECIAL_LF:
            # SO says this, but CLI says no
            # if not flags[Flag.ESCAPE]:
            flags[Flag.QUOTE] = False
            if flags[Flag.ESCAPE]:
                # keep escape, move
                pass
            idx += 1
            continue
        else:
            buff += char
            idx += 1

    if debug:
        return list(flags.items())
    return output
