# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class Common(TestCase):
    def test_loggging_decorator_nolog(self):
        from butch.commands import what_func, LOG_STR
        from butch.context import Context
        from typing import NamedTuple

        dummy_value = 123
        func_name = "dummy"

        self.assertNotIn(func_name, locals())

        @what_func
        def dummy():
            return dummy_value

        self.assertIn(func_name, locals())

        ctx = Context()
        mocked = MagicMock()
        ctx.log.debug = mocked

        self.assertEqual(dummy(), dummy_value)
        mocked.assert_not_called()

    def test_loggging_decorator(self):
        from butch.commands import what_func, LOG_STR
        from butch.context import Context
        from typing import NamedTuple

        dummy_value = 123
        func_name = "dummy"

        self.assertNotIn(func_name, locals())

        @what_func
        def dummy(**__):
            return dummy_value

        self.assertIn(func_name, locals())

        ctx = Context()
        mocked = MagicMock()
        ctx.log.debug = mocked

        self.assertEqual(dummy(ctx=ctx), dummy_value)
        mocked.assert_called_once_with(LOG_STR, func_name, None, ctx)


class EchoCommand(TestCase):
    def test_echo_plain_single(self):
        import sys
        from butch.context import Context
        from butch.commands import echo
        from butch.tokens import Argument

        args = ["a"]

        ctx = Context()
        with patch("builtins.print") as prnt:
            echo(params=[Argument(value=value) for value in args], ctx=ctx)

        prnt.assert_called_once_with(*args, file=sys.stdout)

    def test_echo_plain_multi(self):
        import sys
        from butch.context import Context
        from butch.commands import echo
        from butch.tokens import Argument

        args = ["a", "b", "c"]

        ctx = Context()
        with patch("builtins.print") as prnt:
            echo(params=[Argument(value=value) for value in args], ctx=ctx)

        prnt.assert_called_once_with(*args, file=sys.stdout)

    def test_echo_help(self):
        import sys
        from butch.context import Context
        from butch.commands import echo
        from butch.commandtype import CommandType
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP

        args = ["a", "b", "c"]

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            echo(params=[Argument(value=PARAM_HELP)], ctx=ctx)

        prnt.assert_called_once_with(cmd=CommandType.ECHO, file=sys.stdout)

    def test_echo_onoff(self):
        import sys
        from butch.context import Context
        from butch.commands import echo
        from butch.commandtype import CommandType
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP, ECHO_STATE

        args = ["a", "b", "c"]

        ctx = Context()
        self.assertTrue(ctx.echo)
        echo(params=[Argument(value="off")], ctx=ctx)
        self.assertFalse(ctx.echo)
        with patch("builtins.print") as prnt:
            echo(params=[], ctx=ctx)
            prnt.assert_called_once_with(
                ECHO_STATE.format("off"), file=sys.stdout
            )

        echo(params=[Argument(value="on")], ctx=ctx)
        self.assertTrue(ctx.echo)
        with patch("builtins.print") as prnt:
            echo(params=[], ctx=ctx)
            prnt.assert_called_once_with(
                ECHO_STATE.format("on"), file=sys.stdout
            )

    def test_echo_piped(self):
        import sys
        from butch.context import Context
        from butch.commands import echo
        from butch.tokens import Argument

        dummy = "dummy"

        ctx = Context()
        ctx.collect_output = True
        echo(params=[Argument(value=dummy)], ctx=ctx)

        pipe = ctx.output.stdout
        self.assertEqual(pipe.read(), "")  # no seek
        pipe.seek(0)
        self.assertEqual(pipe.read(), f"{dummy}\n")


class TypeCommand(TestCase):
    def test_type_piped_single(self):
        import sys
        from os.path import abspath
        from butch.context import Context
        from butch.commands import type_cmd
        from butch.tokens import Argument

        dummy = "dummy"

        ctx = Context()
        ctx.collect_output = True
        type_cmd(params=[Argument(value=abspath(__file__))], ctx=ctx)

        pipe = ctx.output.stdout
        self.assertEqual(pipe.read(), "")  # no seek
        pipe.seek(0)
        with open(__file__) as this_file:
            self.assertEqual(pipe.read(), this_file.read() + "\n")

    def test_type_piped_multi(self):
        import sys
        from os.path import abspath
        from butch.context import Context
        from butch.commands import type_cmd
        from butch.tokens import Argument

        dummy = "dummy"

        ctx = Context()
        ctx.collect_output = True
        path = abspath(__file__)
        type_cmd(params=[Argument(value=path)] * 2, ctx=ctx)

        pipe = ctx.output.stdout
        self.assertEqual(pipe.read(), "")  # no seek
        pipe.seek(0)
        with open(__file__) as this_file:
            body = this_file.read()
            self.assertEqual(
                pipe.read(),
                f"{path}\n\n\n\n\n{body}\n\n\n{path}\n\n\n\n\n{body}\n"
            )

    def test_type_no_args(self):
        import sys
        from butch.context import Context
        from butch.constants import SYNTAX_INCORRECT
        from butch.commands import type_cmd

        ctx = Context()
        ctx.collect_output = True
        self.assertEqual(ctx.error_level, 0)
        type_cmd(params=[], ctx=ctx)
        self.assertEqual(ctx.error_level, 1)

        pipe = ctx.output.stdout
        self.assertEqual(pipe.read(), "")  # no seek
        pipe.seek(0)
        self.assertEqual(pipe.read(), SYNTAX_INCORRECT + "\n")

    def test_type_help(self):
        import sys
        from butch.context import Context
        from butch.constants import PARAM_HELP
        from butch.commands import type_cmd
        from butch.commandtype import CommandType
        from butch.tokens import Argument

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            type_cmd(params=[Argument(value=PARAM_HELP)], ctx=ctx)

        prnt.assert_called_once_with(cmd=CommandType.TYPE, file=sys.stdout)

    def test_type_folder(self):
        import sys
        from os.path import abspath, dirname
        from butch.context import Context
        from butch.commands import type_cmd
        from butch.constants import ACCESS_DENIED
        from butch.tokens import Argument

        dummy = "dummy"

        ctx = Context()
        ctx.collect_output = True
        type_cmd(params=[Argument(value=dirname(abspath(__file__)))], ctx=ctx)

        pipe = ctx.output.stdout
        self.assertEqual(pipe.read(), "")  # no seek
        pipe.seek(0)
        with open(__file__) as this_file:
            self.assertEqual(pipe.read(), ACCESS_DENIED + "\n")

    def test_type_nonexisting_single(self):
        import sys
        from os.path import abspath, dirname
        from butch.context import Context
        from butch.commands import type_cmd
        from butch.constants import FILE_NOT_FOUND
        from butch.tokens import Argument

        dummy = "dummy"

        ctx = Context()
        ctx.collect_output = True
        type_cmd(params=[Argument(value=dummy)], ctx=ctx)

        pipe = ctx.output.stdout
        self.assertEqual(pipe.read(), "")  # no seek
        pipe.seek(0)
        with open(__file__) as this_file:
            self.assertEqual(pipe.read(), FILE_NOT_FOUND + "\n")

    def test_type_folder_multi(self):
        import sys
        from os.path import abspath, dirname
        from butch.context import Context
        from butch.commands import type_cmd
        from butch.constants import ACCESS_DENIED, ERROR_PROCESSING
        from butch.tokens import Argument

        dummy = "dummy"

        ctx = Context()
        ctx.collect_output = True
        path = dirname(abspath(__file__))
        type_cmd(params=[Argument(value=path)] * 2, ctx=ctx)

        pipe = ctx.output.stdout
        self.assertEqual(pipe.read(), "")  # no seek
        pipe.seek(0)
        error = ERROR_PROCESSING.format(path)
        self.assertEqual(
            pipe.read(), f"{path}\n{ACCESS_DENIED}\n{error}\n" * 2
        )

    def test_type_nonexisting_multi(self):
        import sys
        from os.path import abspath, dirname
        from butch.context import Context
        from butch.commands import type_cmd
        from butch.constants import FILE_NOT_FOUND, ERROR_PROCESSING
        from butch.tokens import Argument

        dummy = "dummy"

        ctx = Context()
        ctx.collect_output = True
        type_cmd(params=[Argument(value=dummy)] * 2, ctx=ctx)

        pipe = ctx.output.stdout
        self.assertEqual(pipe.read(), "")  # no seek
        pipe.seek(0)
        error = ERROR_PROCESSING.format(dummy)
        self.assertEqual(
            pipe.read(), f"{dummy}\n{FILE_NOT_FOUND}\n{error}\n" * 2
        )


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
