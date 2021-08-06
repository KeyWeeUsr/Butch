# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class PathCommand(TestCase):
    def test_path_stdout(self):
        import sys
        from butch.context import Context
        from butch.commands import path_cmd
        from butch.tokens import Argument

        ctx = Context()
        path = "h%e!l;l/o\\."
        ctx.set_variable("PATH", path)

        with patch("builtins.print") as prnt:
            path_cmd(params=[], ctx=ctx)
        prnt.assert_called_once_with(f"PATH={path}", file=sys.stdout)

    def test_path_piped(self):
        from butch.context import Context
        from butch.commands import path_cmd
        from butch.tokens import Argument

        ctx = Context()
        ctx.collect_output = True
        path = "h%e!l;l/o\\."
        ctx.set_variable("PATH", path)
        path_cmd(params=[], ctx=ctx)

        pipe = ctx.output.stdout
        self.assertEqual(pipe.read(), "")  # no seek
        pipe.seek(0)
        self.assertEqual(pipe.read(), f"PATH={path}\n")

    def test_path_help(self):
        import sys
        from butch.context import Context
        from butch.commands import path_cmd
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP
        from butch.commandtype import CommandType

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            path_cmd(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.PATH, file=sys.stdout)

    def test_path_delete(self):
        from butch.context import Context
        from butch.commands import path_cmd
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP

        ctx = Context()
        self.assertIsNone(ctx.get_variable("PATH"))
        path_cmd(params=[Argument(value=";")], ctx=ctx)
        self.assertEqual(ctx.get_variable("PATH"), "")

        dummy = "butch"
        ctx.set_variable("PATH", dummy)
        self.assertEqual(ctx.get_variable("PATH"), dummy)
        path_cmd(params=[Argument(value=";")], ctx=ctx)
        self.assertEqual(ctx.get_variable("PATH"), "")

    def test_path_set(self):
        from butch.context import Context
        from butch.commands import path_cmd
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP

        ctx = Context()
        new_path = "something"
        self.assertIsNone(ctx.get_variable("PATH"))
        path_cmd(params=[Argument(value=new_path)], ctx=ctx)
        self.assertEqual(ctx.get_variable("PATH"), new_path)

        dummy = "butch"
        ctx.set_variable("PATH", dummy)
        self.assertEqual(ctx.get_variable("PATH"), dummy)
        path_cmd(params=[Argument(value=new_path)], ctx=ctx)
        self.assertEqual(ctx.get_variable("PATH"), new_path)
