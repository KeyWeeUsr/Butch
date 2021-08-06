# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


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
