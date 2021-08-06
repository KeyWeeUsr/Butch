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


class PromptCommand(TestCase):
    def test_prompt_help(self):
        import sys
        from butch.context import Context
        from butch.commands import prompt
        from butch.commandtype import CommandType
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            prompt(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.PROMPT, file=sys.stdout)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            prompt(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.PROMPT, file=ctx.output.stdout
        )

    def test_prompt_empty(self):
        import sys
        from butch.context import Context
        from butch.commands import prompt

        ctx = Context()
        self.assertEqual(ctx.error_level, 0)
        with patch("builtins.print") as prnt:
            prompt(params=[], ctx=ctx)
        prnt.assert_called_once_with(file=sys.stdout)
        self.assertEqual(ctx.error_level, 1)

        ctx.collect_output = True
        ctx.error_level = 0
        self.assertEqual(ctx.error_level, 0)
        with patch("builtins.print") as prnt:
            prompt(params=[], ctx=ctx)
        prnt.assert_called_once_with(file=ctx.output.stdout)
        self.assertEqual(ctx.error_level, 1)

    def test_prompt(self):
        from butch.context import Context, PROMPT_KEY
        from butch.commands import prompt
        from butch.tokens import Argument

        ctx = Context()
        ctx.set_variable = MagicMock()
        dummy = "dummy"

        self.assertEqual(ctx.error_level, 0)
        prompt(params=[Argument(value=dummy)], ctx=ctx)
        self.assertEqual(ctx.error_level, 0)
        ctx.set_variable.assert_called_once_with(
            key=PROMPT_KEY, value_to_set=dummy
        )

        ctx.set_variable = MagicMock()
        ctx.collect_output = True
        ctx.error_level = 0
        self.assertEqual(ctx.error_level, 0)
        prompt(params=[Argument(value=dummy)], ctx=ctx)
        self.assertEqual(ctx.error_level, 0)
        ctx.set_variable.assert_called_once_with(
            key=PROMPT_KEY, value_to_set=dummy
        )


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
        with isdir_mock, patch("butch.context.chdir") as cdir:
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
