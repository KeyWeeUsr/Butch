# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class PushdCommand(TestCase):
    def test_pushd_help(self):
        import sys
        from butch.context import Context
        from butch.commands import pushd
        from butch.commandtype import CommandType
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            pushd(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.PUSHD, file=sys.stdout)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            pushd(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.PUSHD, file=ctx.output.stdout
        )

    def test_pushd_empty(self):
        import sys
        from butch.context import Context
        from butch.commands import pushd

        ctx = Context()
        self.assertEqual(ctx.error_level, 0)
        with patch("builtins.print") as prnt:
            pushd(params=[], ctx=ctx)
        prnt.assert_called_once_with(file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        ctx.error_level = 0
        self.assertEqual(ctx.error_level, 0)
        with patch("builtins.print") as prnt:
            pushd(params=[], ctx=ctx)
        prnt.assert_called_once_with(file=ctx.output.stdout)
        self.assertEqual(ctx.error_level, 0)

    def test_pushd_space_autojoin(self):
        import sys
        from os.path import abspath
        from butch.context import Context
        from butch.commands import pushd
        from butch.tokens import Argument

        ctx = Context()
        path = "path with spaces"

        self.assertEqual(ctx.error_level, 0)
        self.assertEqual(ctx.pushd_history, [])
        isdir_mock = patch("butch.context.isdir", return_value=True)
        exists_mock = patch("butch.context.exists", return_value=True)
        with exists_mock, isdir_mock, patch("butch.context.chdir") as cdir:
            pushd(params=[
                Argument(value=part)
                for part in path.split(" ")
            ], ctx=ctx)
        cdir.assert_called_once_with(path)
        self.assertEqual(ctx.error_level, 0)
        self.assertEqual(ctx.pushd_history, [abspath(path)])

    def test_pushd_file(self):
        import sys
        from os.path import abspath
        from butch.context import Context
        from butch.commands import pushd
        from butch.tokens import Argument

        ctx = Context()
        path = "dummy"

        self.assertEqual(ctx.error_level, 0)
        self.assertEqual(ctx.pushd_history, [])
        isdir_mock = patch("butch.context.isdir", return_value=False)
        with isdir_mock, patch("butch.context.chdir") as cdir:
            pushd(params=[Argument(value=path)], ctx=ctx)
        cdir.assert_not_called()
        self.assertEqual(ctx.error_level, 1)
        self.assertEqual(ctx.pushd_history, [])

    def test_pushd_nonexisting(self):
        import sys
        from os.path import abspath
        from butch.context import Context
        from butch.commands import pushd
        from butch.tokens import Argument
        from butch.constants import PATH_NOT_FOUND

        ctx = Context()
        path = "<nonexisting>"

        self.assertEqual(ctx.error_level, 0)
        self.assertEqual(ctx.pushd_history, [])

        chdir_mock = patch(
            "butch.context.chdir", side_effect=FileNotFoundError
        )
        isdir_mock = patch("butch.context.isdir", return_value=True)
        print_mock = patch("builtins.print")
        with isdir_mock, chdir_mock as cdir, print_mock as prnt:
            pushd(params=[Argument(value=path)], ctx=ctx)
        cdir.assert_called_once_with(path)
        prnt.assert_called_once_with(PATH_NOT_FOUND, file=sys.stderr)
        self.assertEqual(ctx.error_level, 1)
        self.assertEqual(ctx.pushd_history, [])
