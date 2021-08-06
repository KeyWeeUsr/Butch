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
