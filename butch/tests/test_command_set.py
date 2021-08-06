# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


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
