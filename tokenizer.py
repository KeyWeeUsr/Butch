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
