# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class ClsCommand(TestCase):
    def test_cls_help(self):
        import sys
        from butch.context import Context
        from butch.commands import clear_screen
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP
        from butch.commandtype import CommandType

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            clear_screen(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.CLS, file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            clear_screen(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.CLS, file=ctx.output.stdout
        )
        self.assertEqual(ctx.error_level, 0)

    def test_cls_unix(self):
        import sys
        from butch.commands import clear_screen
        from butch.context import Context
        from butch.constants import OCTAL_CLEAR

        ctx = Context()
        with patch("builtins.print") as prnt:
            clear_screen(params=[], ctx=ctx)
        prnt.assert_called_once_with(OCTAL_CLEAR, file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        with patch("builtins.print") as prnt:
            clear_screen(params=[], ctx=ctx)
        prnt.assert_called_once_with(OCTAL_CLEAR, file=ctx.output.stdout)
        self.assertEqual(ctx.error_level, 0)
