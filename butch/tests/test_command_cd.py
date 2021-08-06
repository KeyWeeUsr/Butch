# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class CdCommand(TestCase):
    def test_cd_help(self):
        import sys
        from butch.context import Context
        from butch.commands import cd
        from butch.commandtype import CommandType
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            cd(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.CD, file=sys.stdout)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            cd(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.CD, file=ctx.output.stdout
        )

    def test_cd_home(self):
        from butch.commands import cd
        from butch.context import Context

        dummy = "dummy"

        ctx = Context()
        env_mock = patch("butch.commands.environ.get", return_value=dummy)
        with env_mock, patch("butch.context.chdir") as cdir:
            cd(params=[], ctx=ctx)
        cdir.assert_called_once_with(dummy)

    def test_cd_path(self):
        from butch.commands import cd
        from butch.context import Context
        from butch.tokens import Argument

        dummy = "dummy"

        ctx = Context()
        with patch("butch.context.chdir") as cdir:
            cd(params=[Argument(value=dummy)], ctx=ctx)
        cdir.assert_called_once_with(dummy)
        self.assertEqual(ctx.error_level, 0)

    def test_cd_nonexisting(self):
        import sys
        from butch.commands import cd
        from butch.context import Context
        from butch.tokens import Argument
        from butch.constants import PATH_NOT_FOUND

        path = "<nonexisting>"

        ctx = Context()
        print_mock = patch("butch.commands.print")
        chdir_mock = patch(
            "butch.context.chdir", side_effect=FileNotFoundError
        )
        with chdir_mock as cdir, print_mock as prnt:
            cd(params=[Argument(value=path)], ctx=ctx)
        cdir.assert_called_once_with(path)
        prnt.assert_called_once_with(PATH_NOT_FOUND, file=sys.stderr)
        self.assertEqual(ctx.error_level, 1)
