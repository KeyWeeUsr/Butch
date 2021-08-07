# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class PauseCommand(TestCase):
    def test_pause_help(self):
        import sys
        from butch.context import Context
        from butch.commands import pause
        from butch.commandtype import CommandType
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            pause(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.PAUSE, file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            pause(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.PAUSE, file=ctx.output.stdout
        )
        self.assertEqual(ctx.error_level, 0)

    def test_pause(self):
        import sys
        from butch.context import Context
        from butch.commands import pause
        from butch.tokens import Argument
        from butch.constants import PAUSE_TEXT

        ctx = Context()
        dummy = "dummy"

        with patch("builtins.input") as inp:
            pause(params=[Argument(value=dummy)], ctx=ctx)
        inp.assert_called_once_with(PAUSE_TEXT)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        with patch("builtins.input") as inp:
            pause(params=[Argument(value=dummy)], ctx=ctx)
        inp.assert_called_once_with(PAUSE_TEXT)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = False
        with patch("builtins.input") as inp:
            pause(params=[], ctx=ctx)
        inp.assert_called_once_with(PAUSE_TEXT)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        with patch("builtins.input") as inp:
            pause(params=[], ctx=ctx)
        inp.assert_called_once_with(PAUSE_TEXT)
        self.assertEqual(ctx.error_level, 0)
