# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class RemCommand(TestCase):
    def test_rem_help(self):
        import sys
        from butch.context import Context
        from butch.commands import rem_comment
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP
        from butch.commandtype import CommandType

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            rem_comment(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.REM, file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            rem_comment(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.REM, file=ctx.output.stdout
        )
        self.assertEqual(ctx.error_level, 0)

    def test_rem_comment(self):
        from butch.context import Context
        from butch.commands import rem_comment
        from butch.tokens import Argument

        ctx = Context()
        dummy = [Argument(value="dummy")]
        with patch("builtins.print") as prnt:
            rem_comment(params=dummy, ctx=ctx)
        prnt.assert_not_called()
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        with patch("builtins.print") as prnt:
            rem_comment(params=dummy, ctx=ctx)
        prnt.assert_not_called()
        self.assertEqual(ctx.error_level, 0)

    def test_rem_empty(self):
        from butch.context import Context
        from butch.commands import rem_comment

        ctx = Context()
        with patch("builtins.print") as prnt:
            rem_comment(params=[], ctx=ctx)
        prnt.assert_not_called()
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        with patch("builtins.print") as prnt:
            rem_comment(params=[], ctx=ctx)
        prnt.assert_not_called()
        self.assertEqual(ctx.error_level, 0)
