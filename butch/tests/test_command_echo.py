# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class EchoCommand(TestCase):
    def test_echo_plain_single(self):
        import sys
        from butch.context import Context
        from butch.commands import echo
        from butch.tokens import Argument

        args = ["a"]

        ctx = Context()
        with patch("builtins.print") as prnt:
            echo(params=[Argument(value=value) for value in args], ctx=ctx)

        prnt.assert_called_once_with(*args, file=sys.stdout)

    def test_echo_plain_multi(self):
        import sys
        from butch.context import Context
        from butch.commands import echo
        from butch.tokens import Argument

        args = ["a", "b", "c"]

        ctx = Context()
        with patch("builtins.print") as prnt:
            echo(params=[Argument(value=value) for value in args], ctx=ctx)

        prnt.assert_called_once_with(*args, file=sys.stdout)

    def test_echo_help(self):
        import sys
        from butch.context import Context
        from butch.commands import echo
        from butch.commandtype import CommandType
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP

        args = ["a", "b", "c"]

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            echo(params=[Argument(value=PARAM_HELP)], ctx=ctx)

        prnt.assert_called_once_with(cmd=CommandType.ECHO, file=sys.stdout)

    def test_echo_onoff(self):
        import sys
        from butch.context import Context
        from butch.commands import echo
        from butch.commandtype import CommandType
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP, ECHO_STATE

        args = ["a", "b", "c"]

        ctx = Context()
        self.assertTrue(ctx.echo)
        echo(params=[Argument(value="off")], ctx=ctx)
        self.assertFalse(ctx.echo)
        with patch("builtins.print") as prnt:
            echo(params=[], ctx=ctx)
            prnt.assert_called_once_with(
                ECHO_STATE.format("off"), file=sys.stdout
            )

        echo(params=[Argument(value="on")], ctx=ctx)
        self.assertTrue(ctx.echo)
        with patch("builtins.print") as prnt:
            echo(params=[], ctx=ctx)
            prnt.assert_called_once_with(
                ECHO_STATE.format("on"), file=sys.stdout
            )

    def test_echo_piped(self):
        import sys
        from butch.context import Context
        from butch.commands import echo
        from butch.tokens import Argument

        dummy = "dummy"

        ctx = Context()
        ctx.collect_output = True
        echo(params=[Argument(value=dummy)], ctx=ctx)

        pipe = ctx.output.stdout
        self.assertEqual(pipe.read(), "")  # no seek
        pipe.seek(0)
        self.assertEqual(pipe.read(), f"{dummy}\n")
