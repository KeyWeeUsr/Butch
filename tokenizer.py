from collections import defaultdict
from enum import Enum, auto
from context import Context
from commands import Command as CommandType, get_reverse_cmd_map
from grammar import *
from counter import Count
from filmbuffer import FilmBuffer
from charlist import CharList
from shared import Shared


EMPTYF = lambda *_: None

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
    """Shouldn't be used directly, but ABC might be overkill."""
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

    @right.setter
    def right(self, value):
        self._right = value

    def __repr__(self):
        return f'<{self.name}: [{self.left}, {self.right}]>'


class Concat(Connector):
    def __init__(self, left: Command, right: Command = None):
        super().__init__("Concat", left=left, right=right)


class Pipe(Connector):
    def __init__(self, left: Command, right: Command = None):
        super().__init__("Pipe", left=left, right=right)


class RedirType(Enum):
    INPUT = auto()
    OUTPUT = auto()


class Redirection(Connector):
    _type: RedirType
    _append: bool = False

    def __init__(
            self, redir_type: RedirType,
            left: Command, right: Command = None,
            append: bool = False
    ):
        super().__init__("Redirection", left=left, right=right)
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


def handle_char_cr(pos: Count, ctx: Context = None, log=EMPTYF) -> None:
    log("- is <CR>")
    next(pos)


def handle_char_carret(
        pos: Count, flags: dict, ctx: Context = None, log=EMPTYF
) -> None:
    log("- is carret, enabling escape flag")
    flags[Flag.ESCAPE] = True
    next(pos)


def handle_char_quote(
        pos: Count, flags: dict, text: FilmBuffer,
        buff: CharList, output: list, found: Shared,
        ctx: Context = None, log=EMPTYF
) -> None:
    prev_white = text.pchar in DELIM_WHITE
    if prev_white and not flags[Flag.WORD] and not flags[Flag.QUOTE]:
        log("- is word, enabling word flag")
        flags[Flag.WORD] = True

    log("- is quote, swapping quote flag")
    flags[Flag.QUOTE] = not flags[Flag.QUOTE]

    if text.pchar not in DELIM_WHITE and flags[Flag.QUOTE]:
        log("- is quote in the middle of word")
        flags[Flag.QUOTE_IN_WORD] = True

    log("\t- quote: %s", flags[Flag.QUOTE])
    next(pos)
    if not flags[Flag.QUOTE] and flags[Flag.WORD]:
        log("\t- unquoting")
        buff += QUOTE_DOUBLE
        log("-> %r", buff)

        if found:
            log("\t\t- found command")
            found.data.args = found.data.args + [
                Argument(
                    value=buff.data,
                    quoted=True and not flags[Flag.QUOTE_IN_WORD]
                )
            ]
            log("\t\t- appending to output: %r", found)
            output.append(found.data)
            if text.nchar == SPECIAL_LF:
                # keep to collect quoted but mangled
                # "name="ignored -> 1 arg later unquoted in cmd func
                # and 'ignored' part would be stripped
                found.clear()
            else:
                flags[Flag.UNFINISHED_LINE] = True
        if text.nchar in DELIM_WHITE:
            log("\t- unwording, next char is white")
            flags[Flag.WORD] = False
            log("- unquoting middle quote")
            flags[Flag.QUOTE_IN_WORD] = False
        if text.nchar in SPECIAL_LF:
            log("\t- unwording, next char is <LF>")
            flags[Flag.WORD] = False
        buff.clear()
    else:
        buff += QUOTE_DOUBLE


def handle_char_ordinary(
        pos: Count, flags: dict, text: FilmBuffer,
        buff: CharList, output: list,
        ctx: Context = None, log=EMPTYF
) -> None:
    log("- not matching, increment + append")
    splitnext = text.nchar in SPECIAL_SPLITTERS
    idx = pos.value

    if idx == 0:
        log("\t- word flag on, idx == 0")
        flags[Flag.WORD] = True
    elif text.pchar in DELIM_WHITE and not splitnext and not flags[Flag.QUOTE]:
        log("\t- word flag on, pchar is white")
        flags[Flag.WORD] = True

    if splitnext:
        log("\t- appending to output before splitting")
        flags[Flag.WORD] = False
        output.append(found_command.data)
        found_command.clear()
    buff += text.char
    next(pos)


def handle_char_newline(
        pos: Count, flags: dict, text: FilmBuffer,
        buff: CharList, output: list, found: Shared,
        compound: Count, ctx: Context = None, log=EMPTYF
) -> None:
    log("- is <LF>, disabling quote flag")
    # SO says this, but CLI says no
    # if not flags[Flag.ESCAPE]:
    flags[Flag.QUOTE] = False
    cmd_map = get_reverse_cmd_map()

    if flags[Flag.ESCAPE]:
        log("\t- is in escape mode")
        # keep escape, move
        next(pos)
        return

    log("\t- is not in escape mode")
    # reverse me later to "if not" + main
    if pos.value == text.last_pos and buff:  # buff check for whitespace
        log("\t\t- last char")
        if not found:
            cmd_clear = buff.data.strip().lower()
            echo = True
            if cmd_clear.startswith("@"):
                log("\t\t- echo off")
                echo = False
                cmd_clear = cmd_clear[1:]
            log("\t- cmd string: %r", cmd_clear)
            found.set(Command(
                cmd=cmd_map.get(cmd_clear, CommandType.UNKNOWN),
                echo=echo
            ))
            buff.clear()
        if buff:
            found.data.args = found.data.args + [
                Argument(value=buff.data)
            ]
        buff.clear()
        if not output:
            log("\t\t- appending to output: %r", found)
            output.append(found.data)
        else:
            log("\t\t- output present, check if connector")
            last = output[-1]
            if isinstance(last, Connector) and not last.right:
                log("\t\t\t- is connector w/ empty r-val")
                log("\t\t\t\t- insert: %r", found)
                output[-1].right = found.data
                found.clear()
            else:
                log(
                    "\t\t\t- not connector, appending: %r",
                    found
                )
                output.append(found.data)
                found.clear()
    if pos.value != text.last_pos and buff:  # buff check for whitespace
        log("\t\t- not last char, %r", buff)
        if not found:
            found.set(Command(cmd=CommandType.UNKNOWN))
        if flags[Flag.UNFINISHED_LINE]:
            found.data.args[-1].value = (
                found.data.args[-1].value + buff.data
            )
            flags[Flag.UNFINISHED_LINE] = False
        else:
            found.data.args = found.data.args + [
                Argument(value=buff.data)
            ]

            if not output:
                log("\t\t- appending to output: %r", found)
                output.append(found.data)
            else:
                log("\t\t- output present, check if connector")
                last = output[-1]
                if isinstance(last, Connector) and not last.right:
                    log("\t\t\t- is connector w/ empty r-val")
                    log("\t\t\t\t- insert: %r", found)
                    output[-1].right = found.data
                    found.clear()
                else:
                    log(
                        "\t\t\t- not connector, appending: %r",
                        found
                    )
                    output.append(found.data)
                    found.clear()

        buff.clear()
        found.clear()

    if compound > 0:
        # do not move to the next line,
        # join buff to single command
        pass

    next(pos)


def tokenize(text: str, ctx: Context, debug: bool = False) -> list:
    log = ctx.log.debug
    log("Starting tokenization")
    from parser import percent_expansion
    output = []

    idx = Count()
    text = FilmBuffer(data=text)
    text_len = len(text)
    last_pos = text.last_pos

    cmd_map = get_reverse_cmd_map()
    flags = defaultdict(bool)
    compound = Count()

    fword = Flag.WORD
    fquot = Flag.QUOTE
    fqinw = Flag.QUOTE_IN_WORD

    buff = CharList()
    found_command = Shared()

    while idx.value < text_len:
        text.move(idx.value)
        char = text.char
        log("Position: (end=%04d, idx=%04d, char=%r)", last_pos, idx.value, char)
        log("- flags: %r", flags)
        log("- buff: %r", buff)

        pchar = text.pchar
        nchar = text.nchar

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
                found_command.set(Command(cmd=CommandType.UNKNOWN))
            if found_command:
                log("\t- found command")
                found_command.data.args = found_command.data.args + [
                    Argument(value=buff.data)
                ]
                buff.clear()
                log("\t- appending to output: %r", found_command)
                output.append(found_command.data)
            break

        if char == SPECIAL_CR:
            handle_char_cr(pos=idx, log=log)
        elif char == SPECIAL_CARRET:
            handle_char_carret(pos=idx, flags=flags, log=log)
        elif char == QUOTE_DOUBLE:
            handle_char_quote(
                pos=idx, flags=flags,
                text=text, buff=buff, output=output,
                found=found_command, log=log
            )
        elif char == SPECIAL_LF:
            handle_char_newline(
                pos=idx, flags=flags,
                text=text, buff=buff, output=output,
                found=found_command, compound=compound, log=log
            )
        elif char in SPECIAL_SPLITTERS:
            log("- is splitter")
            last = output[-1] if output else None
            if last and not isinstance(last, Command):
                log("\t- left isn't command, assuming splitter")
                log("\t- assuming argument leftovers in buffer")

                # cmd1 [arg ...] | cmd2 [arg ...] | cmd3 [arg ...]
                # \---parse---> P(P(1 | 2) | 3)
                #
                # P----(L)---P--(L)---1
                #  \          \
                #   \          \(R)---2
                #    \
                #     \(R)------------3
                if buff:
                    last.right.args = last.right.args + [
                        Argument(value=buff.data)
                    ]
            elif found_command:
                # command not yet added, assembling now
                log("\t- found_command: %r", found_command)
                last = found_command.data
            join = None
            if char == SPECIAL_PIPE:
                log("\t- is pipe")
                if nchar == SPECIAL_PIPE:
                    log("\t\t- is double-pipe (OR)")
                    join = Concat(left=last)
                    next(idx)
                else:
                    log("\t\t- is normal pipe")
                    join = Pipe(left=last)
            elif char == SPECIAL_AMP:
                log("\t- is amp")
                join = Concat(left=last)
                if nchar == SPECIAL_AMP:
                    log("\t\t- is &&")
                    next(idx)
            elif char in SPECIAL_REDIR:
                log("\t- is redirection")
                append = False
                if nchar in SPECIAL_REDIR:
                    append = True
                    next(idx)
                join = Redirection(left=last, right=None, append=append)
            # the last command is now encapsulated in a connector
            # the newest command is stored in the "right" branch
            log("\t- check output: %r", output)
            if output:
                log("\t- attaching command to connector")
                output[-1] = join
            else:
                log("\t- creating new item: %r", join)
                output.append(join)
            found_command.clear()
            next(idx)
        elif char == SPECIAL_LPAREN:
            log("- is left-paren")
            next(compound)
            next(idx)
        elif char == SPECIAL_RPAREN:
            log("- is right-paren")
            flags[Flag.WORD] = False
            reversed(compound)
            next(idx)
        elif char in DELIM_WHITE:
            log("- is whitespace")
            if flags[Flag.QUOTE]:
                log("\t- is quoted")
                buff += char
                next(idx)
                continue
            if not found_command and buff:
                log("\t- not found command")

                # naive
                cmd_clear = buff.data.strip().lower()
                echo = True
                if cmd_clear.startswith("@"):
                    log("\t\t- echo off")
                    echo = False
                    cmd_clear = cmd_clear[1:]
                log("\t- cmd string: %r", cmd_clear)
                found_command.set(Command(
                    cmd=cmd_map.get(cmd_clear, CommandType.UNKNOWN), echo=echo
                ))
                buff.clear()
            elif found_command:
                log("\t- found command")
                if not flags[Flag.QUOTE]:
                    log("\t\t- not in quote mode")
                    found_command.data.args = found_command.data.args + [
                        Argument(value=buff.data)
                    ]
                    buff.clear()
            flags[Flag.WORD] = False
            next(idx)
        else:
            handle_char_ordinary(
                pos=idx, flags=flags, text=text, buff=buff,
                output=output, log=log
            )

    if debug:
        return list(flags.items())
    log("- tokenized output: %r", output)
    return output
