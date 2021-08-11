# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class VerCommand(TestCase):
    def test_ver_help(self):
        import sys
        from butch.context import Context
        from butch.commands import cmd_ver
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP
        from butch.commandtype import CommandType

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            cmd_ver(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.VER, file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            cmd_ver(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.VER, file=ctx.output.stdout
        )
        self.assertEqual(ctx.error_level, 0)

    def test_ver_platform(self):
        import sys
        from butch.context import Context
        from butch.commands import cmd_ver
        from butch.tokens import Argument

        ctx = Context()
        dummy = "dummy"

        ctx.error_level = 123
        self.assertEqual(ctx.error_level, 123)
        platform_mock = patch("butch.commands.platform", return_value=dummy)
        print_mock = patch("builtins.print")
        with platform_mock as plf, print_mock as prnt:
            self.assertIsNone(cmd_ver(params=[], ctx=ctx))
        plf.assert_called_once_with()
        prnt.assert_called_once_with(dummy, file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.error_level = 123
        self.assertEqual(ctx.error_level, 123)
        platform_mock = patch("butch.commands.platform", return_value=dummy)
        print_mock = patch("builtins.print")
        with platform_mock as plf, print_mock as prnt:
            self.assertIsNone(cmd_ver(params=[Argument(value="abc")], ctx=ctx))
        plf.assert_called_once_with()
        prnt.assert_called_once_with(dummy, file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        ctx.error_level = 123
        self.assertEqual(ctx.error_level, 123)
        platform_mock = patch("butch.commands.platform", return_value=dummy)
        print_mock = patch("builtins.print")
        with platform_mock as plf, print_mock as prnt:
            self.assertIsNone(cmd_ver(params=[], ctx=ctx))
        plf.assert_called_once_with()
        prnt.assert_called_once_with(dummy, file=ctx.output.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        ctx.error_level = 123
        self.assertEqual(ctx.error_level, 123)
        platform_mock = patch("butch.commands.platform", return_value=dummy)
        print_mock = patch("builtins.print")
        with platform_mock as plf, print_mock as prnt:
            self.assertIsNone(cmd_ver(params=[Argument(value="abc")], ctx=ctx))
        plf.assert_called_once_with()
        prnt.assert_called_once_with(dummy, file=ctx.output.stdout)
        self.assertEqual(ctx.error_level, 0)
