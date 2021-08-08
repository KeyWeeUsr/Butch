# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class ExitCommand(TestCase):
    def test_exit_help(self):
        import sys
        from butch.context import Context
        from butch.commands import exit_cmd
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP
        from butch.commandtype import CommandType

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            exit_cmd(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.EXIT, file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            exit_cmd(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.EXIT, file=ctx.output.stdout
        )
        self.assertEqual(ctx.error_level, 0)

    def test_exit_all(self):
        from butch.context import Context
        from butch.commands import exit_cmd

        with patch("sys.exit") as ext:
            exit_cmd(params=[], ctx=Context())
        ext.assert_called_once_with(0)

    def test_exit_current_script(self):
        from butch.context import Context
        from butch.commands import exit_cmd
        from butch.tokens import Argument

        ctx = Context()
        ctx.error_level = 123
        self.assertEqual(ctx.error_level, 123)

        status = 456
        with patch("sys.exit") as ext:
            exit_cmd(params=[
                Argument(value="/B"), Argument(value=str(status))
            ], ctx=ctx)
        ext.assert_called_once_with(status)
        self.assertEqual(ctx.error_level, status)

    def test_exit_current_script_wob(self):
        from butch.context import Context
        from butch.commands import exit_cmd
        from butch.tokens import Argument

        ctx = Context()
        ctx.error_level = 123
        self.assertEqual(ctx.error_level, 123)

        status = 456
        with patch("sys.exit") as ext:
            exit_cmd(params=[Argument(value=str(status))], ctx=ctx)
        ext.assert_called_once_with(status)
        self.assertEqual(ctx.error_level, status)
