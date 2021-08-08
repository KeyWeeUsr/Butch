# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class DirCommand(TestCase):
    def test_dir_help(self):
        import sys
        from butch.context import Context
        from butch.commands import list_folder
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP
        from butch.commandtype import CommandType

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            list_folder(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.DIR, file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            list_folder(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.DIR, file=ctx.output.stdout
        )
        self.assertEqual(ctx.error_level, 0)

    def test_dir_nie(self):
        import sys
        from butch.context import Context
        from butch.commands import list_folder
        from butch.tokens import Argument
        from butch.commandtype import CommandType

        ctx = Context()
        dummy = [Argument(value="dummy")]
        print_mock = patch("builtins.print")
        help_mock = patch("butch.commands.print_help")
        nie = self.assertRaises(NotImplementedError)

        with print_mock as prnt, help_mock as halp, nie:
            list_folder(params=dummy, ctx=ctx)
        prnt.assert_not_called()
        halp.assert_not_called()
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        with print_mock as prnt, help_mock as halp, nie:
            list_folder(params=dummy, ctx=ctx)
        prnt.assert_not_called()
        halp.assert_not_called()
        self.assertEqual(ctx.error_level, 0)

    def test_dir_empty(self):
        import sys
        from butch.context import Context
        from butch.commands import list_folder
        from butch.commandtype import CommandType

        ctx = Context()
        lines = ["a", "b", "c"]
        print_mock = patch("builtins.print")
        get_lines_mock = patch(
            "butch.commands._get_listdir_lines", return_value=lines
        )
        cwd_mock = patch("butch.commands.getcwd")
        with print_mock as prnt, get_lines_mock as get, cwd_mock as cwd:
            list_folder(params=[], ctx=ctx)
        get.assert_called_once_with(folder=cwd.return_value, ctx=ctx)
        prnt.assert_called_once_with("\n".join(lines), file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        print_mock = patch("builtins.print")
        get_lines_mock = patch(
            "butch.commands._get_listdir_lines", return_value=lines
        )
        cwd_mock = patch("butch.commands.getcwd")
        with print_mock as prnt, get_lines_mock as get, cwd_mock as cwd:
            list_folder(params=[], ctx=ctx)
        get.assert_called_once_with(folder=cwd.return_value, ctx=ctx)
        prnt.assert_called_once_with("\n".join(lines), file=ctx.output.stdout)
        self.assertEqual(ctx.error_level, 0)
