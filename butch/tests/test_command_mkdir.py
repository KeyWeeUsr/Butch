# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class MkdirCommand(TestCase):
    def test_mkdir_help(self):
        import sys
        from butch.context import Context
        from butch.commands import create_folder
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP
        from butch.commandtype import CommandType

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            create_folder(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.MKDIR, file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            create_folder(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.MKDIR, file=ctx.output.stdout
        )
        self.assertEqual(ctx.error_level, 0)

    def test_mkdir_empty(self):
        import sys
        from butch.context import Context
        from butch.commands import create_folder
        from butch.constants import SYNTAX_INCORRECT

        ctx = Context()
        with patch("builtins.print") as prnt:
            create_folder(params=[], ctx=ctx)
        prnt.assert_called_once_with(SYNTAX_INCORRECT, file=sys.stderr)
        self.assertEqual(ctx.error_level, 1)

        ctx.collect_output = True
        ctx.error_level = 0
        with patch("builtins.print") as prnt:
            create_folder(params=[], ctx=ctx)
        prnt.assert_called_once_with(SYNTAX_INCORRECT, file=sys.stderr)
        self.assertEqual(ctx.error_level, 1)
