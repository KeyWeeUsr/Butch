# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class GotoCommand(TestCase):
    def test_goto_help(self):
        import sys
        from butch.context import Context
        from butch.commands import goto
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP
        from butch.commandtype import CommandType

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            goto(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.GOTO, file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            goto(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.GOTO, file=ctx.output.stdout
        )
        self.assertEqual(ctx.error_level, 0)

    def test_goto_without_label(self):
        from butch.context import Context
        from butch.commands import goto

        ctx = Context()
        self.assertEqual(ctx.error_level, 0)
        self.assertIsNone(goto(params=[], ctx=ctx))
        self.assertEqual(ctx.error_level, 1)

    def test_goto_colon_eof(self):
        from butch.context import Context
        from butch.commands import goto
        from butch.jumptype import JumpTypeEof
        from butch.tokens import Argument

        ctx = Context()
        self.assertEqual(ctx.error_level, 0)
        self.assertIsNone(ctx.jump)
        self.assertIsNone(goto(params=[Argument(value=":eof")], ctx=ctx))
        self.assertEqual(ctx.jump, JumpTypeEof())
        self.assertEqual(ctx.error_level, 0)
