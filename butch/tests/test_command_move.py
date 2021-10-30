# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, call


class MoveCommand(TestCase):
    def test_move_help(self):
        import sys
        from butch.context import Context
        from butch.commands import cmd_move
        from butch.commandtype import CommandType
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            cmd_move(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.MOVE, file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            cmd_move(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.MOVE, file=ctx.output.stdout
        )
        self.assertEqual(ctx.error_level, 0)

    def test_move_miss_to_miss(self):
        import sys
        from butch.context import Context
        from butch.commands import cmd_move
        from butch.tokens import Argument
        from butch.constants import FILE_NOT_FOUND
        from os.path import exists

        ctx = Context()
        dummy = "dummy"

        self.assertFalse(exists(dummy))
        self.assertFalse(exists(f"{dummy}2"))
        with patch("builtins.print") as stderr:
            cmd_move(
                params=[Argument(value=dummy), Argument(value=f"{dummy}2")],
                ctx=ctx
            )
            stderr.assert_called_once_with(FILE_NOT_FOUND, file=sys.stderr)
        self.assertFalse(exists(dummy))
        self.assertFalse(exists(f"{dummy}2"))
        self.assertEqual(ctx.error_level, 1)
