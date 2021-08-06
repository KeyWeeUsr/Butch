# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class PopdCommand(TestCase):
    def test_popd_help(self):
        import sys
        from butch.context import Context
        from butch.commands import popd
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP
        from butch.commandtype import CommandType

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            popd(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.POPD, file=sys.stdout)

    def test_popd_help_piped(self):
        import sys
        from butch.context import Context
        from butch.commands import popd
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP
        from butch.commandtype import CommandType

        ctx = Context()
        ctx.collect_output = True

        with patch("butch.commands.print_help") as prnt:
            popd(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        pipe = ctx.output.stdout
        prnt.assert_called_once_with(cmd=CommandType.POPD, file=pipe)

    def test_popd_normal(self):
        import sys
        from butch.context import Context
        from butch.commands import popd
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP
        from butch.commandtype import CommandType

        dummy = "dummy"
        ctx = Context()
        ctx.pop_folder = MagicMock(return_value=dummy)
        with patch("butch.context.chdir") as cdir:
            popd(params=[], ctx=ctx)
        ctx.pop_folder.assert_called_once_with()
        cdir.assert_called_once_with(dummy)

    def test_popd_nonexisting(self):
        import sys
        from butch.context import Context
        from butch.commands import popd
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP
        from butch.commandtype import CommandType

        dummy = "dummy"
        ctx = Context()
        ctx.pop_folder = MagicMock(return_value=dummy)
        chdir_mock = patch(
            "butch.context.chdir", side_effect=FileNotFoundError
        )
        with chdir_mock as cdir:
            popd(params=[], ctx=ctx)
        ctx.pop_folder.assert_called_once_with()
        cdir.assert_called_once_with(dummy)

    def test_popd_empty_stack(self):
        import sys
        from butch.context import Context
        from butch.commands import popd
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP
        from butch.commandtype import CommandType

        dummy = "dummy"
        ctx = Context()
        ctx.pop_folder = MagicMock(side_effect=IndexError)
        popd(params=[], ctx=ctx)
        ctx.pop_folder.assert_called_once_with()
