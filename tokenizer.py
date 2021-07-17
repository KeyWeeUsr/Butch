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
    WORD = auto()
    QUOTE_IN_WORD = auto()
    UNFINISHED_LINE = auto()


class Argument:
    _value: str = ""
    _quoted: bool = False

    def __init__(self, value: str, quoted: bool = False):
        self._value = value
        self._quoted = quoted

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def quoted(self):
        return self._quoted

    def __repr__(self):
        val = self._value
        if self.quoted:
            val = repr(val)
        return f'<Argument: {val!r}, q={int(self.quoted)}>'

    def __eq__(self, other):
        return self.value == other.value


class Command:
    _cmd: CommandType = None
    _name: str = ""
    _value: str = ""
    _echo: bool = True
    _args: list = None

    def __init__(
            self, cmd: CommandType, args: list = [],
            value: str = "", echo: bool = True
    ):
        self._cmd = cmd
        self._name = cmd.value
        self._value = value
        self._args = args
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
    def args(self):
        return self._args

    @args.setter
    def args(self, value: list):
        self._args = value

    @property
    def echo(self):
        return self._echo

    def __repr__(self):
        prefix = "@" if not self.echo else ""
        return f'<{prefix}Command: "{self.name}" {self.args}>'


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


def tokenize(text: str, ctx: Context, debug: bool = False) -> list:
    log = ctx.log.debug
    log("Starting tokenization")
    from parser import percent_expansion
    output = []

    idx = 0

    text_len = len(text)
    last_pos = text_len - 1
    cmd_map = get_reverse_cmd_map()
    flags = defaultdict(bool)
    compound_count = 0

    fword = Flag.WORD
    fquot = Flag.QUOTE
    fqinw = Flag.QUOTE_IN_WORD
    funfi = Flag.UNFINISHED_LINE

    buff = ""
    found_command = None
    while idx < text_len:
        char = text[idx]
        log("Position: (end=%04d, idx=%04d, char=%r)", last_pos, idx, char)
        log("- flags: %r", flags)
        log("- buff: %r", buff)

        pchar = ""
        nchar = ""
        if idx > 0:
            pchar = text[idx - 1]
        if idx < last_pos:
            nchar = text[idx + 1]

        # last char isn't <LF>
        if char != SPECIAL_LF and idx == last_pos:
            log("- last char")
            buff += char.replace("\r", "")

            if not buff:
                break

            if char == SPECIAL_CARRET:
                log("\t- is carret, enabling escape flag")
                flags[Flag.ESCAPE] = True
            elif char == QUOTE_DOUBLE:
                log("\t- is quote, swapping quote flag")
                flags[fquot] = not flags[fquot]
                log("\t\t- quote: %s", flags[fquot])
            # append last char because finishing
            # and if buff is empty (single-char), then copy char to buff
            if idx == 0:
                log("\t- not found command, zero idx")
                found_command = Command(cmd=CommandType.UNKNOWN)
            if found_command:
                log("\t- found command")
                found_command.args = found_command.args + [
                    Argument(value=buff)
                ]
                buff = ""
                output.append(found_command)
            break

        if char == SPECIAL_CR:
            log("- is <CR>")
            idx += 1
        elif char == SPECIAL_CARRET:
            log("- is carret, enabling escape flag")
            flags[Flag.ESCAPE] = True
            idx += 1
        elif char == QUOTE_DOUBLE:
            if pchar in DELIM_WHITE and not flags[fword] and not flags[fquot]:
                log("- is word, enabling word flag")
                flags[Flag.WORD] = True
            log("- is quote, swapping quote flag")
            flags[fquot] = not flags[fquot]
            if pchar not in DELIM_WHITE and flags[fquot]:
                log("- is quote in the middle of word")
                flags[fqinw] = True
            log("\t- quote: %s", flags[Flag.QUOTE])
            idx += 1
            if not flags[fquot] and flags[fword]:
                log("\t- unquoting")
                buff += QUOTE_DOUBLE
                log("-> %r", buff)

                if found_command:
                    log("\t\t- found command")
                    found_command.args = found_command.args + [
                        Argument(
                            value=buff,
                            quoted=True and not flags[fqinw]
                        )
                    ]
                    output.append(found_command)
                    if nchar == SPECIAL_LF:
                        # keep to collect quoted but mangled
                        # "name="ignored -> 1 arg later unquoted in cmd func
                        # and 'ignored' part would be stripped
                        found_command = None
                    else:
                        flags[funfi] = True
                if nchar in DELIM_WHITE:
                    log("\t- unwording, next char is white")
                    flags[fword] = False
                    log("- unquoting middle quote")
                    flags[fqinw] = False
                if nchar in SPECIAL_LF:
                    log("\t- unwording, next char is <LF>")
                    flags[fword] = False
                buff = ""
            else:
                buff += QUOTE_DOUBLE
        elif char == SPECIAL_LF:
            log("- is <LF>, disabling quote flag")
            # SO says this, but CLI says no
            # if not flags[Flag.ESCAPE]:
            flags[Flag.QUOTE] = False
            if flags[Flag.ESCAPE]:
                log("\t- is in escape mode")
                # keep escape, move
                pass
            else:
                log("\t- is not in escape mode")
                # reverse me later to "if not" + main
                if idx == last_pos and buff:  # buff check for whitespace
                    log("\t\t- last char")
                    if not found_command:
                        cmd_clear = buff.strip().lower()
                        echo = True
                        if cmd_clear.startswith("@"):
                            log("\t\t- echo off")
                            echo = False
                            cmd_clear = cmd_clear[1:]
                        log("\t- cmd string: %r", cmd_clear)
                        found_command = Command(
                            cmd=cmd_map.get(cmd_clear, CommandType.UNKNOWN),
                            echo=echo
                        )
                        buff = ""
                    if buff:
                        found_command.args = found_command.args + [
                            Argument(value=buff)
                        ]
                    buff = ""
                    output.append(found_command)
                if idx != last_pos and buff:  # buff check for whitespace
                    log("\t\t- not last char, %r", buff)
                    if not found_command:
                        found_command = Command(cmd=CommandType.UNKNOWN)
                    if flags[funfi]:
                        found_command.args[-1].value = (
                            found_command.args[-1].value + buff
                        )
                        flags[funfi] = False
                    else:
                        found_command.args = found_command.args + [
                            Argument(value=buff)
                        ]
                        output.append(found_command)
                    buff = ""
                    found_command = None

            if compound_count > 0:
                # do not move to the next line,
                # join buff to single command
                pass

            
            idx += 1
        elif char in SPECIAL_SPLITTERS:
            log("- is splitter (TBD)")
            left = Command(name="???", value=buff)
            right = ...
            join = None
            if char == SPECIAL_PIPE:
                log("\t- is pipe")
                if nchar == SPECIAL_PIPE:
                    log("\t\t- is double-pipe (OR)")
                    join = Concat(left=left, right=right)
                else:
                    log("\t\t- is normal pipe")
                    join = Pipe(left=left, right=right)
            elif char == SPECIAL_AMP:
                log("\t- is amp")
                join = Concat(left=left, right=right)
            elif char in SPECIAL_REDIR:
                log("\t- is redirection")
                join = Redirection(
                    left=left, right=right,
                    append=nchar in SPECIAL_REDIR
                )
        elif char == SPECIAL_LPAREN:
            log("- is left-paren")
            compound_count += 1
            idx += 1
        elif char == SPECIAL_RPAREN:
            log("- is right-paren")
            flags[Flag.WORD] = False
            compound_count -= 1
            idx += 1
        elif char in DELIM_WHITE:
            log("- is whitespace")
            if flags[Flag.QUOTE]:
                log("\t- is quoted")
                buff += char
                idx += 1
                continue
            if not found_command and buff:
                log("\t- not found command")

                # naive
                cmd_clear = buff.strip().lower()
                echo = True
                if cmd_clear.startswith("@"):
                    log("\t\t- echo off")
                    echo = False
                    cmd_clear = cmd_clear[1:]
                log("\t- cmd string: %r", cmd_clear)
                found_command = Command(
                    cmd=cmd_map.get(cmd_clear, CommandType.UNKNOWN),
                    echo=echo
                )
                buff = ""
            elif found_command:
                log("\t- found command")
                if not flags[Flag.QUOTE]:
                    log("\t\t- not in quote mode")
                    found_command.args = found_command.args + [
                        Argument(value=buff)
                    ]
                    buff = ""
            flags[Flag.WORD] = False
            idx += 1
        else:
            log("- not matching, increment + append")
            if idx == 0:
                log("\t- word flag on, idx == 0")
                flags[fword] = True
            elif pchar in DELIM_WHITE and not flags[fquot]:
                log("\t- word flag on, pchar is white")
                flags[fword] = True
            buff += char
            idx += 1

    if debug:
        return list(flags.items())
    log("- tokenized output: %r", output)
    return output
