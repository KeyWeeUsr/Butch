# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class TimeCommand(TestCase):
    def test_time_help(self):
        import sys
        from butch.context import Context
        from butch.commands import time
        from butch.commandtype import CommandType
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            time(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.TIME, file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            time(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.TIME, file=ctx.output.stdout
        )
        self.assertEqual(ctx.error_level, 0)

    def test_time_print_only(self):
        import sys
        from butch.context import Context
        from butch.commands import time
        from butch.tokens import Argument

        ctx = Context()
        time_mock = patch("butch.commands.datetime")
        with time_mock as dmock, patch("builtins.print") as prnt:
            time(params=[Argument(value="/t")], ctx=ctx)
        dmock.now.assert_called_once_with()
        strf = dmock.now.return_value.strftime
        strf.assert_called_once_with("%X")
        prnt.assert_called_once_with(strf.return_value, file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        time_mock = patch("butch.commands.datetime")
        with time_mock as dmock, patch("builtins.print") as prnt:
            time(params=[Argument(value="/T")], ctx=ctx)
        dmock.now.assert_called_once_with()
        strf = dmock.now.return_value.strftime
        strf.assert_called_once_with("%X")
        prnt.assert_called_once_with(strf.return_value, file=ctx.output.stdout)
        self.assertEqual(ctx.error_level, 0)

    def test_time_print_ask(self):
        import sys
        from butch.context import Context
        from butch.commands import time

        ctx = Context()
        time_mock = patch("butch.commands.datetime")
        print_mock = patch("builtins.print")
        input_mock = patch("builtins.input")
        with time_mock as dmock, print_mock as prnt, input_mock as inp:
            time(params=[], ctx=ctx)
        dmock.now.assert_called_once_with()
        strf = dmock.now.return_value.strftime
        strf.assert_called_once_with("%X")
        buffers = [
            mock_call.kwargs["file"]
            for mock_call in prnt.call_args_list
        ]
        self.assertEqual(buffers, [sys.stdout] * 2 + [sys.stderr])
        inp.assert_called_once_with()
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        time_mock = patch("butch.commands.datetime")
        print_mock = patch("builtins.print")
        input_mock = patch("builtins.input")
        with time_mock as dmock, print_mock as prnt, input_mock as inp:
            time(params=[], ctx=ctx)
        dmock.now.assert_called_once_with()
        strf = dmock.now.return_value.strftime
        strf.assert_called_once_with("%X")
        buffers = [
            mock_call.kwargs["file"]
            for mock_call in prnt.call_args_list
        ]
        self.assertEqual(buffers, [ctx.output.stdout] * 2 + [sys.stderr])
        inp.assert_called_once_with()
        self.assertEqual(ctx.error_level, 0)

    def test_time_print_interrupt(self):
        import sys
        from butch.context import Context
        from butch.commands import time

        ctx = Context()
        time_mock = patch("butch.commands.datetime")
        print_mock = patch("builtins.print")
        input_mock = patch("builtins.input", side_effect=KeyboardInterrupt)
        with time_mock as dmock, print_mock as prnt, input_mock as inp:
            time(params=[], ctx=ctx)
        dmock.now.assert_called_once_with()
        strf = dmock.now.return_value.strftime
        strf.assert_called_once_with("%X")
        buffers = [
            mock_call.kwargs["file"]
            for mock_call in prnt.call_args_list
        ]
        self.assertEqual(buffers, [sys.stdout] * 2 + [sys.stderr])
        inp.assert_called_once_with()
        self.assertEqual(ctx.error_level, 1)

        ctx.collect_output = True
        time_mock = patch("butch.commands.datetime")
        print_mock = patch("builtins.print")
        input_mock = patch("builtins.input", side_effect=KeyboardInterrupt)
        with time_mock as dmock, print_mock as prnt, input_mock as inp:
            time(params=[], ctx=ctx)
        dmock.now.assert_called_once_with()
        strf = dmock.now.return_value.strftime
        strf.assert_called_once_with("%X")
        buffers = [
            mock_call.kwargs["file"]
            for mock_call in prnt.call_args_list
        ]
        self.assertEqual(buffers, [ctx.output.stdout] * 2 + [sys.stderr])
        inp.assert_called_once_with()
        self.assertEqual(ctx.error_level, 1)
