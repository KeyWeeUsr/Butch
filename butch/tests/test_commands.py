# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class HelpCommand(TestCase):
    def test_help_itself(self):
        import sys
        from butch.context import Context
        from butch.commands import help_cmd
        from butch.commandtype import CommandType

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            help_cmd(params=[], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.HELP, file=sys.stdout)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            help_cmd(params=[], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.HELP, file=ctx.output.stdout
        )

    def test_help_from_arg(self):
        import sys
        from butch.context import Context
        from butch.commands import help_cmd
        from butch.tokens import Argument
        from butch.commandtype import CommandType

        prefix = "butch.commands"
        map_str = f"{prefix}.get_reverse_cmd_map"
        print_str = f"{prefix}.print_help"

        ctx = Context()
        dummy = "DuMmY"
        with patch(map_str) as cmd_map, patch(print_str) as prnt:
            help_cmd(params=[Argument(value=dummy)], ctx=ctx)
        cmd_map.return_value.get.assert_called_once_with(
            dummy.lower(), CommandType.UNKNOWN
        )
        prnt.assert_called_once_with(
            cmd=cmd_map.return_value.get.return_value, file=sys.stdout
        )

        ctx.collect_output = True
        with patch(map_str) as cmd_map, patch(print_str) as prnt:
            help_cmd(params=[Argument(value=dummy)], ctx=ctx)
        cmd_map.return_value.get.assert_called_once_with(
            dummy.lower(), CommandType.UNKNOWN
        )
        prnt.assert_called_once_with(
            cmd=cmd_map.return_value.get.return_value, file=ctx.output.stdout
        )


class Utils(TestCase):
    def test_print_all_vars(self):
        import sys
        from butch.context import Context
        from butch.commands import _print_all_variables
        from unittest.mock import call

        ctx = Context()
        with patch("butch.commands.print") as prnt:
            _print_all_variables(ctx=ctx, file=sys.stdout)
            self.assertEqual(prnt.call_count, len(ctx.variables))

    def test_print_single_var_undefined(self):
        import sys
        from butch.context import Context
        from butch.commands import _print_single_variable
        from butch.constants import ENV_VAR_UNDEFINED
        from unittest.mock import call

        ctx = Context()
        ctx.get_variable = MagicMock(return_value=False)

        dummy = "dummy"
        with patch("butch.commands.print") as prnt:
            _print_single_variable(key=dummy, ctx=ctx, file=sys.stdout)
        prnt.assert_called_once_with(ENV_VAR_UNDEFINED, file=sys.stdout)
        ctx.get_variable.assert_called_once_with(key=dummy)

    def test_print_single_var_defined(self):
        import sys
        from butch.context import Context
        from butch.commands import _print_single_variable
        from unittest.mock import call

        ctx = Context()
        found_value = "found"
        ctx.get_variable = MagicMock(return_value=found_value)

        dummy = "dummy"
        with patch("butch.commands.print") as prnt:
            _print_single_variable(key=dummy, ctx=ctx, file=sys.stdout)
        prnt.assert_called_once_with(f"{dummy}={found_value}", file=sys.stdout)
        ctx.get_variable.assert_called_once_with(key=dummy)


class SetCommand(TestCase):
    def test_set_help(self):
        import sys
        from butch.context import Context
        from butch.commands import set_cmd
        from butch.tokens import Argument
        from butch.commandtype import CommandType
        from butch.constants import PARAM_HELP

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            set_cmd(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.SET, file=sys.stdout)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            set_cmd(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.SET, file=ctx.output.stdout
        )

    def test_set_print_all(self):
        import sys
        from butch.context import Context
        from butch.commands import set_cmd
        from butch.commandtype import CommandType

        ctx = Context()
        with patch("butch.commands._print_all_variables") as prnt:
            set_cmd(params=[], ctx=ctx)
        prnt.assert_called_once_with(ctx=ctx, file=sys.stdout)

        ctx.collect_output = True
        with patch("butch.commands._print_all_variables") as prnt:
            set_cmd(params=[], ctx=ctx)
        prnt.assert_called_once_with(ctx=ctx, file=ctx.output.stdout)

    def test_set_prompt_with_text(self):
        import sys
        from butch.context import Context
        from butch.commands import set_cmd
        from butch.tokens import Argument
        from butch.commandtype import CommandType

        ctx = Context()
        key = "myvar"
        prompt = "my prompt"
        prompt_input = "butch"
        with patch("builtins.input", return_value=prompt_input):
            set_cmd(params=[
                Argument(value="/P"), Argument(value=f"{key}={prompt}")
            ], ctx=ctx)
        self.assertEqual(ctx.get_variable(key=key), prompt_input)

    def test_set_prompt_quiet(self):
        import sys
        from butch.context import Context
        from butch.commands import set_cmd
        from butch.tokens import Argument
        from butch.commandtype import CommandType

        ctx = Context()
        key = "myvar"
        prompt_input = "butch"
        with patch("builtins.input", return_value=prompt_input):
            set_cmd(params=[
                Argument(value="/P"), Argument(value=f"{key}=")
            ], ctx=ctx)
        self.assertEqual(ctx.get_variable(key=key), prompt_input)

    def test_set_prompt_from_stdin(self):
        import sys
        from butch.context import Context
        from butch.commands import set_cmd
        from butch.inputs import CommandInput
        from butch.tokens import Argument
        from butch.commandtype import CommandType

        ctx = Context()
        input_obj = CommandInput()
        ctx.input = input_obj

        key = "myvar"
        prompt = "my prompt"
        prompt_input = "butch"
        input_obj.stdin.write(prompt_input + "\n")
        input_obj.stdin.seek(0)

        input_mock = patch("builtins.input")
        ctx.inputted = True
        with input_mock as inp, patch("builtins.print") as prnt:
            set_cmd(params=[
                Argument(value="/P"), Argument(value=f"{key}={prompt}")
            ], ctx=ctx)
        inp.assert_not_called()
        prnt.assert_called_once_with(prompt, file=sys.stdout)
        self.assertEqual(ctx.get_variable(key=key), prompt_input)

    def test_set_prompt_empty_from_stdin(self):
        import sys
        from butch.context import Context
        from butch.commands import set_cmd
        from butch.inputs import CommandInput
        from butch.tokens import Argument
        from butch.commandtype import CommandType

        ctx = Context()
        input_obj = CommandInput()
        ctx.input = input_obj

        prompt = "my prompt"

        input_mock = patch("builtins.input")
        ctx.inputted = True
        with input_mock as inp, patch("builtins.print") as prnt:
            set_cmd(params=[
                Argument(value="/P"), Argument(value=f"myvar={prompt}")
            ], ctx=ctx)
        inp.assert_not_called()
        prnt.assert_called_once_with(prompt, file=sys.stdout)
        self.assertEqual(ctx.error_level, 1)

    def test_set_prompt_from_stdin_quiet(self):
        import sys
        from butch.context import Context
        from butch.commands import set_cmd
        from butch.inputs import CommandInput
        from butch.tokens import Argument
        from butch.commandtype import CommandType

        ctx = Context()
        input_obj = CommandInput()
        ctx.input = input_obj

        key = "myvar"
        prompt_input = "butch"
        input_obj.stdin.write(prompt_input + "\n")
        input_obj.stdin.seek(0)

        input_mock = patch("builtins.input")
        ctx.inputted = True
        with input_mock as inp, patch("builtins.print") as prnt:
            set_cmd(params=[
                Argument(value="/P"), Argument(value=f"{key}=")
            ], ctx=ctx)
        inp.assert_not_called()
        prnt.assert_not_called()
        self.assertEqual(ctx.get_variable(key=key), prompt_input)

    def test_set_prompt_empty_from_stdin_quiet(self):
        import sys
        from butch.context import Context
        from butch.commands import set_cmd
        from butch.inputs import CommandInput
        from butch.tokens import Argument
        from butch.commandtype import CommandType

        ctx = Context()
        input_obj = CommandInput()
        ctx.input = input_obj

        input_mock = patch("builtins.input")
        ctx.inputted = True
        with input_mock as inp, patch("builtins.print") as prnt:
            set_cmd(params=[
                Argument(value="/P"), Argument(value="myvar=")
            ], ctx=ctx)
        inp.assert_not_called()
        prnt.assert_not_called()
        self.assertEqual(ctx.error_level, 1)

    def test_set_delete(self):
        import sys
        from butch.context import Context
        from butch.commands import set_cmd
        from butch.inputs import CommandInput
        from butch.tokens import Argument
        from butch.commandtype import CommandType

        ctx = Context()
        key = "myvar"
        ctx.set_variable(key=key, value_to_set="dummy")
        set_cmd(params=[Argument(value=f"{key}=")], ctx=ctx)
        self.assertEqual(ctx.error_level, 0)
        self.assertEqual(ctx.get_variable(key=key), "")

    def test_set_value(self):
        import sys
        from butch.context import Context
        from butch.commands import set_cmd
        from butch.inputs import CommandInput
        from butch.tokens import Argument
        from butch.commandtype import CommandType

        ctx = Context()
        key = "myvar"
        dummy = "dummy"
        ctx.set_variable(key=key, value_to_set=dummy)
        set_cmd(params=[Argument(value=f"{key}={dummy}")], ctx=ctx)
        self.assertEqual(ctx.error_level, 0)
        self.assertEqual(ctx.get_variable(key=key), dummy)

    def test_set_print_single(self):
        import sys
        from butch.context import Context
        from butch.commands import set_cmd
        from butch.outputs import CommandOutput
        from butch.tokens import Argument
        from butch.commandtype import CommandType

        ctx = Context()
        key = "myvar"
        dummy = "dummy"
        ctx.set_variable(key=key, value_to_set=dummy)
        with patch("butch.commands._print_single_variable") as prnt:
            set_cmd(params=[Argument(value=key)], ctx=ctx)
        prnt.assert_called_once_with(key=key, ctx=ctx, file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        ctx.output = CommandOutput()
        with patch("butch.commands._print_single_variable") as prnt:
            set_cmd(params=[Argument(value=key)], ctx=ctx)
        prnt.assert_called_once_with(key=key, ctx=ctx, file=ctx.output.stdout)
        self.assertEqual(ctx.error_level, 0)

    def test_set_value_quoted(self):
        import sys
        from butch.context import Context
        from butch.commands import set_cmd
        from butch.inputs import CommandInput
        from butch.tokens import Argument
        from butch.commandtype import CommandType

        ctx = Context()
        key = "my var"
        dummy = "dummy"
        ctx.set_variable(key=key, value_to_set=dummy)
        set_cmd(params=[
            Argument(value=f"{key}={dummy}", quoted=True)
        ], ctx=ctx)
        self.assertEqual(ctx.error_level, 0)
        self.assertEqual(ctx.get_variable(key=key), dummy)


class SetlocalCommand(TestCase):
    def test_setlocal_help(self):
        import sys
        from butch.context import Context
        from butch.commands import setlocal
        from butch.commandtype import CommandType
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            setlocal(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.SETLOCAL, file=sys.stdout)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            setlocal(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.SETLOCAL, file=ctx.output.stdout
        )

    def test_setlocal_enable_expansion(self):
        from butch.context import Context
        from butch.commands import setlocal
        from butch.tokens import Argument

        ctx = Context()
        ctx.delayed_expansion_enabled = False
        self.assertFalse(ctx.delayed_expansion_enabled)
        setlocal(params=[Argument(value="enabledelayedexpansion")], ctx=ctx)
        self.assertTrue(ctx.delayed_expansion_enabled)

    def test_setlocal_disable_expansion(self):
        from butch.context import Context
        from butch.commands import setlocal
        from butch.tokens import Argument

        ctx = Context()
        ctx.delayed_expansion_enabled = True
        self.assertTrue(ctx.delayed_expansion_enabled)
        setlocal(params=[Argument(value="disabledelayedexpansion")], ctx=ctx)
        self.assertFalse(ctx.delayed_expansion_enabled)

    def test_setlocal_enable_extensions(self):
        from butch.context import Context
        from butch.commands import setlocal
        from butch.tokens import Argument

        ctx = Context()
        ctx.extensions_enabled = False
        self.assertFalse(ctx.extensions_enabled)
        setlocal(params=[Argument(value="enableextensions")], ctx=ctx)
        self.assertTrue(ctx.extensions_enabled)

    def test_setlocal_disable_extensions(self):
        from butch.context import Context
        from butch.commands import setlocal
        from butch.tokens import Argument

        ctx = Context()
        ctx.extensions_enabled = True
        self.assertTrue(ctx.extensions_enabled)
        setlocal(params=[Argument(value="disableextensions")], ctx=ctx)
        self.assertFalse(ctx.extensions_enabled)

    def test_setlocal_unknown(self):
        from butch.context import Context
        from butch.commands import setlocal
        from butch.tokens import Argument

        ctx = Context()
        self.assertFalse(ctx.delayed_expansion_enabled)
        self.assertTrue(ctx.extensions_enabled)
        setlocal(params=[Argument(value="unknown")], ctx=ctx)
        self.assertFalse(ctx.delayed_expansion_enabled)
        self.assertTrue(ctx.extensions_enabled)

    def test_setlocal_nyi(self):
        from butch.context import Context
        from butch.commands import setlocal
        from butch.tokens import Argument

        ctx = Context()
        with self.assertRaises(NotImplementedError):
            setlocal(params=[], ctx=ctx)


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
