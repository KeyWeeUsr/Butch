"""
Module holding all tokens and tokenizing functions for converting an inputted
Batch code into a set of instructions for the interpreter to execute.
"""

from collections import defaultdict
from enum import Enum, auto

from butch.context import Context
from butch.commands import get_reverse_cmd_map
from butch.commandtype import CommandType
from butch.grammar import (
    SPECIAL_CR, SPECIAL_CARRET, SPECIAL_LPAREN, SPECIAL_RPAREN, SPECIAL_AMP,
    SPECIAL_PIPE, SPECIAL_LT, SPECIAL_REDIR, SPECIAL_SPLITTERS, SPECIAL_LF,
    DELIM_WHITE, QUOTE_DOUBLE, SPECIAL_COLON
)
from butch.counter import Count
from butch.filmbuffer import FilmBuffer
from butch.charlist import CharList
from butch.shared import Shared
from butch.tokens import Argument


def emptyf(*_, **__):
    "Empty function that does nothing."


def clear_input(value: str) -> str:
    "Clear input line if it contains specific chars."
    if set(value) in (set(""), set("\n"), set("\r\n"), set("\n\r"), set(" ")):
        return ""
    return value


class Flag(Enum):
    "Enum of tokenizer flags when parsing the Batch code."
    ESCAPE = auto()
    QUOTE = auto()
    WORD = auto()
    QUOTE_IN_WORD = auto()
    UNFINISHED_LINE = auto()
    COLON_COMMENT = auto()
    COLON_LABEL = auto()


class File:
    "Token holding the raw value of filename for redirection."

    _value: str = ""

    def __init__(self, value: str = ""):
        self._value = value

    @property
    def value(self):
        "Property: raw argument value."
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def __repr__(self):
        val = self._value
        return f"<File: {val!r}>"

    def __eq__(self, other):
        if not isinstance(other, File):
            return False
        return self.value == other.value


class Command:
    "Token holding the raw value of a command and its properties."

    _cmd: CommandType = None
    _name: str = ""
    _value: str = ""
    _echo: bool = True
    _args: list = None

    def __init__(
            # pylint: disable=dangerous-default-value
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
        "Property: CommandType value of the Command token."
        return self._cmd

    @property
    def name(self):
        "Property: raw command name."
        return self._name

    @property
    def value(self):
        "TODO: seems to be unused, perhaps just cmd.value -> name replacement."
        return self._value

    @property
    def args(self):
        "Property: list of Argument tokens."
        return self._args

    @args.setter
    def args(self, value: list):
        self._args = value

    @property
    def echo(self):
        "Property: whether the command should be printed out."
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
        "Property: name of the connector (e.g. Pipe)"
        return self._name

    @property
    def left(self):
        "Property: L-val of a connector char."
        return self._left

    @property
    def right(self):
        "Property: R-val of a connector char."
        return self._right

    @right.setter
    def right(self, value):
        self._right = value

    def __repr__(self):
        return f"<{self.name}: [{self.left}, {self.right}]>"


class Concat(Connector):
    "Token holding the raw value of a concatenation and its properties."

    def __init__(self, left: Command, right: Command = None):
        super().__init__("Concat", left=left, right=right)


class Pipe(Connector):
    "Token holding the raw value of a pipe and its properties."

    def __init__(self, left: Command, right: Command = None):
        super().__init__("Pipe", left=left, right=right)


class RedirType(Enum):
    "Enum to distinguish between redirection out of or into a command/file."
    INPUT = auto()
    OUTPUT = auto()


class Redirection(Connector):
    "Token holding the raw value of a redirection and its properties."

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
        "Property: input or output."
        return self._type

    @property
    def append(self):
        "Property: if the redirection should append or overwrite the target."
        return self._append

    def __repr__(self):
        direction = "?"
        if self.type == RedirType.INPUT:
            direction = "<"
        elif self.type == RedirType.OUTPUT:
            direction = ">"
        if self.append:
            direction *= 2
        return f"<{self.name}: {self.left} {direction} {self.right}>"


def handle_char_cr(pos: Count, ctx: Context = None, log=emptyf) -> None:
    # pylint: disable=unused-argument
    "Handle a <CR> character while parsing an input line."
    log("- is <CR>")
    next(pos)


def handle_char_carret(
        # pylint: disable=unused-argument
        pos: Count, flags: dict, ctx: Context = None, log=emptyf
) -> None:
    "Handle a ^ character while parsing an input line."
    log("- is carret, enabling escape flag")
    flags[Flag.ESCAPE] = True
    next(pos)


def handle_char_quote(
        pos: Count, flags: dict, text: FilmBuffer,
        buff: CharList, output: list, found: Shared,
        log=emptyf
) -> None:
    'Handle a "(double-quote) character while parsing an input line.'
    # pylint: disable=too-many-arguments
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
            if text.nchar == SPECIAL_LF:
                # keep to collect quoted but mangled
                # "name="ignored -> 1 arg later unquoted in cmd func
                # and 'ignored' part would be stripped
                log("\t\t- appending to output: %r", found.data)
                output.append(found.data)
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
        # pylint: disable=too-many-arguments
        pos: Count, flags: dict, text: FilmBuffer,
        buff: CharList, output: list, found: Shared,
        log=emptyf
) -> None:
    "Handle an ordinary character while parsing an input line."
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
        output.append(found.data)
        found.clear()
    buff += text.char
    next(pos)


def handle_char_newline(
        # pylint: disable=too-many-arguments
        pos: Count, flags: dict, text: FilmBuffer,
        buff: CharList, output: list, found: Shared,
        compound: Count, log=emptyf
) -> None:
    "Handle a LF character while parsing an input line."
    # pylint: disable=too-many-statements, too-many-branches
    log("- is <LF>, disabling quote flag")
    # SO says this, but CLI says no
    # if not flags[Flag.ESCAPE]:
    flags[Flag.QUOTE] = False
    flags[Flag.COLON_COMMENT] = False
    flags[Flag.COLON_LABEL] = False
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
                cmd=cmd_map.get(cmd_clear, CommandType.UNKNOWN), echo=echo
            ))
            buff.clear()
        if buff:
            found.data.args = found.data.args + [
                Argument(value=buff.data)
            ]
        buff.clear()
        if not output:
            log("\t\t- appending to output: %r", found.data)
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
                    found.data
                )
                output.append(found.data)
                found.clear()
    if pos.value != text.last_pos and buff:  # buff check for whitespace
        log("\t\t- not last char, %r", buff)
        if not found:
            log("\t\t\t- not found")
            if output and isinstance(output[-1], Redirection):
                log("\t\t\t\t- last item in output is redirection")
                found.set(File())
            else:
                # naive
                cmd_clear = buff.data.strip().lower()
                echo = True
                if cmd_clear.startswith("@"):
                    log("\t\t- echo off")
                    echo = False
                    cmd_clear = cmd_clear[1:]
                log("\t- cmd string: %r", cmd_clear)
                cmd_type = cmd_map.get(cmd_clear, CommandType.UNKNOWN)
                found.set(Command(cmd=cmd_type, echo=echo))
                buff.clear()

        if flags[Flag.UNFINISHED_LINE]:
            log("\t\t\t- unfinished line")
            if not isinstance(found.data, File):
                found.data.args[-1].value = (
                    found.data.args[-1].value + buff.data
                )
            else:
                found.data.value = buff.data
        else:
            log("\t\t\t- finished line")
            if not isinstance(found.data, File):
                log("\t\t\t\t- setting args %r", buff.data)
                if buff.data:
                    found.data.args = found.data.args + [
                        Argument(value=buff.data)
                    ]
            else:
                found.data.value = buff.data

        flags[Flag.UNFINISHED_LINE] = False
        if not output:
            log("\t\t- appending to output: %r", found.data)
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
                    found.data
                )
                output.append(found.data)
                found.clear()

        buff.clear()
        found.clear()

    if compound > 0:
        # do not move to the next line,
        # join buff to single command
        pass

    flags[Flag.COLON_COMMENT] = False
    next(pos)


def handle_char_whitespace(
        # pylint: disable=too-many-arguments
        pos: Count, flags: dict, text: FilmBuffer,
        buff: CharList, found: Shared, log=emptyf
) -> None:
    "Handle a whitespace character while parsing an input line."
    log("- is whitespace")
    if flags[Flag.QUOTE]:
        log("\t- is quoted")
        buff += text.char
        next(pos)
        return

    cmd_map = get_reverse_cmd_map()
    if not found and buff:
        log("\t- not found command")

        # naive
        cmd_clear = buff.data.strip().lower()
        echo = True
        if cmd_clear.startswith("@"):
            log("\t\t- echo off")
            echo = False
            cmd_clear = cmd_clear[1:]
        log("\t- cmd string: %r", cmd_clear)
        found.set(Command(
            cmd=cmd_map.get(cmd_clear, CommandType.UNKNOWN), echo=echo
        ))
        buff.clear()
    elif found:
        log("\t- found command")
        if not flags[Flag.QUOTE]:
            log("\t\t- not in quote mode")
            found.data.args = found.data.args + [
                Argument(value=buff.data)
            ]
            buff.clear()
    flags[Flag.WORD] = False
    next(pos)


def handle_char_splitter(
        pos: Count, text: FilmBuffer, buff: CharList,
        output: list, found: Shared, log=emptyf
) -> None:
    "Handle a command splitting character while parsing an input line."
    # pylint: disable=too-many-arguments
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
    elif found:
        # command not yet added, assembling now
        log("\t- found_command: %r", found)
        last = found.data

    join = None
    char = text.char
    nchar = text.nchar
    if char == SPECIAL_PIPE:
        log("\t- is pipe")
        if nchar == SPECIAL_PIPE:
            log("\t\t- is double-pipe (OR)")
            join = Concat(left=last)
            next(pos)
        else:
            log("\t\t- is normal pipe")
            join = Pipe(left=last)
    elif char == SPECIAL_AMP:
        log("\t- is amp")
        join = Concat(left=last)
        if nchar == SPECIAL_AMP:
            log("\t\t- is &&")
            next(pos)
    elif char in SPECIAL_REDIR:
        log("\t- is redirection")
        append = False
        if nchar in SPECIAL_REDIR:
            append = True
            next(pos)
        join = Redirection(
            redir_type=(
                RedirType.INPUT
                if char == SPECIAL_LT
                else RedirType.OUTPUT
            ),
            left=last, right=None, append=append
        )
    # the last command is now encapsulated in a connector
    # the newest command is stored in the "right" branch
    log("\t- check output: %r", output)
    if output and isinstance(output[-1], Connector):
        log("\t- attaching command to connector")
        output[-1] = join
    else:
        log("\t- creating new item: %r", join)
        output.append(join)
    found.clear()
    next(pos)


def handle_char_last(
        pos: Count, flags: dict, text: FilmBuffer,
        buff: CharList, output: list, found: Shared, log=emptyf
) -> None:
    "Handle the last character of an input line."
    # pylint: disable=too-many-arguments,too-many-statements,too-many-branches
    log("- last char")
    char = text.char
    buff += char.replace("\r", "")

    if not buff or not clear_input(buff.data):
        return

    if char == SPECIAL_CARRET:
        log("\t- is carret, enabling escape flag")
        flags[Flag.ESCAPE] = True
    elif char == QUOTE_DOUBLE:
        log("\t- is quote, swapping quote flag")
        flags[Flag.QUOTE] = not flags[Flag.QUOTE]
        log("\t\t- quote: %s", flags[Flag.QUOTE])
    # append last char because finishing
    # and if buff is empty (single-char), then copy char to buff
    if pos.value == 0:
        log("\t- not found command, zero idx")
        found.set(Command(cmd=CommandType.UNKNOWN))

    cmd_map = get_reverse_cmd_map()
    if pos.value == text.last_pos and buff:  # buff check for whitespace
        if not found:
            cmd_clear = buff.data.strip().lower()
            echo = True
            if cmd_clear.startswith("@"):
                log("\t- echo off")
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
            log("\t- appending to output: %r", found.data)
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
                    found.data
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
                log("\t\t- appending to output: %r", found.data)
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
                        found.data
                    )
                    output.append(found.data)
                    found.clear()

        buff.clear()
        found.clear()


def handle_char_colon(
        pos: Count, flags: dict, text: FilmBuffer, found: Shared, log=emptyf
) -> None:
    """Handle the colon prefix for label or comment."""
    log("- colon")
    nchar = text.nchar

    if nchar == SPECIAL_COLON:
        flags[Flag.COLON_COMMENT] = True
        found.set(Command(cmd=CommandType.REM))
        next(pos)
    elif nchar != SPECIAL_COLON and not flags[Flag.COLON_COMMENT]:
        flags[Flag.COLON_LABEL] = True
    next(pos)


def tokenize(text: str, ctx: Context, debug: bool = False) -> list:
    "Convert Batch as text input into tokens."
    log = ctx.log.debug
    log("Starting tokenization")
    output = []

    idx = Count()
    # replace 0x1A with LF
    text = FilmBuffer(data=text.replace("\x1a", "\n"))
    last_pos = text.last_pos

    flags = defaultdict(bool)
    compound = Count()

    buff = CharList()
    found_command = Shared()

    while idx.value < len(text):
        text.move(idx.value)
        char = text.char
        log(
            "Position: (end=%04d, idx=%04d, char=%r)",
            last_pos, idx.value, char
        )
        log("- flags: %r", flags)
        log("- buff: %r", buff)

        # last char isn't <LF>
        if char != SPECIAL_LF and idx == last_pos:
            handle_char_last(
                pos=idx, flags=flags,
                text=text, buff=buff, output=output,
                found=found_command, log=log
            )
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
            handle_char_splitter(
                pos=idx, text=text, buff=buff, output=output,
                found=found_command, log=log
            )
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
            handle_char_whitespace(
                pos=idx, flags=flags, text=text, buff=buff,
                found=found_command, log=log
            )
        elif char == SPECIAL_COLON and not flags[Flag.COLON_COMMENT]:
            handle_char_colon(
                pos=idx, flags=flags, text=text, found=found_command, log=log
            )
        else:
            handle_char_ordinary(
                pos=idx, flags=flags, text=text, buff=buff,
                output=output, log=log, found=found_command
            )

    if debug:
        return list(flags.items())
    log("- tokenized output: %r", output)
    return output
