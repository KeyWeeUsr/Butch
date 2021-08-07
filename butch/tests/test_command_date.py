# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class DateCommand(TestCase):
    def test_date_help(self):
        import sys
        from butch.context import Context
        from butch.commands import date
        from butch.commandtype import CommandType
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            date(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.DATE, file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            date(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.DATE, file=ctx.output.stdout
        )
        self.assertEqual(ctx.error_level, 0)

    def test_date_print_only(self):
        import sys
        from butch.context import Context
        from butch.commands import date
        from butch.tokens import Argument

        ctx = Context()
        date_mock = patch("butch.commands.datetime")
        with date_mock as dmock, patch("builtins.print") as prnt:
            date(params=[Argument(value="/t")], ctx=ctx)
        dmock.now.assert_called_once_with()
        strf = dmock.now.return_value.strftime
        strf.assert_called_once_with("%x")
        prnt.assert_called_once_with(strf.return_value, file=sys.stdout)
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        date_mock = patch("butch.commands.datetime")
        with date_mock as dmock, patch("builtins.print") as prnt:
            date(params=[Argument(value="/T")], ctx=ctx)
        dmock.now.assert_called_once_with()
        strf = dmock.now.return_value.strftime
        strf.assert_called_once_with("%x")
        prnt.assert_called_once_with(strf.return_value, file=ctx.output.stdout)
        self.assertEqual(ctx.error_level, 0)

    def test_date_print_ask(self):
        import sys
        from butch.context import Context
        from butch.commands import date

        ctx = Context()
        date_mock = patch("butch.commands.datetime")
        print_mock = patch("builtins.print")
        input_mock = patch("builtins.input")
        with date_mock as dmock, print_mock as prnt, input_mock as inp:
            date(params=[], ctx=ctx)
        dmock.now.assert_called_once_with()
        strf = dmock.now.return_value.strftime
        strf.assert_called_once_with("%a %x")
        buffers = [
            mock_call.kwargs["file"]
            for mock_call in prnt.call_args_list
        ]
        self.assertEqual(buffers, [sys.stdout] * 2 + [sys.stderr])
        inp.assert_called_once_with()
        self.assertEqual(ctx.error_level, 0)

        ctx.collect_output = True
        date_mock = patch("butch.commands.datetime")
        print_mock = patch("builtins.print")
        input_mock = patch("builtins.input")
        with date_mock as dmock, print_mock as prnt, input_mock as inp:
            date(params=[], ctx=ctx)
        dmock.now.assert_called_once_with()
        strf = dmock.now.return_value.strftime
        strf.assert_called_once_with("%a %x")
        buffers = [
            mock_call.kwargs["file"]
            for mock_call in prnt.call_args_list
        ]
        self.assertEqual(buffers, [ctx.output.stdout] * 2 + [sys.stderr])
        inp.assert_called_once_with()
        self.assertEqual(ctx.error_level, 0)

    def test_date_print_interrupt(self):
        import sys
        from butch.context import Context
        from butch.commands import date

        ctx = Context()
        date_mock = patch("butch.commands.datetime")
        print_mock = patch("builtins.print")
        input_mock = patch("builtins.input", side_effect=KeyboardInterrupt)
        with date_mock as dmock, print_mock as prnt, input_mock as inp:
            date(params=[], ctx=ctx)
        dmock.now.assert_called_once_with()
        strf = dmock.now.return_value.strftime
        strf.assert_called_once_with("%a %x")
        buffers = [
            mock_call.kwargs["file"]
            for mock_call in prnt.call_args_list
        ]
        self.assertEqual(buffers, [sys.stdout] * 2 + [sys.stderr])
        inp.assert_called_once_with()
        self.assertEqual(ctx.error_level, 1)

        ctx.collect_output = True
        date_mock = patch("butch.commands.datetime")
        print_mock = patch("builtins.print")
        input_mock = patch("builtins.input", side_effect=KeyboardInterrupt)
        with date_mock as dmock, print_mock as prnt, input_mock as inp:
            date(params=[], ctx=ctx)
        dmock.now.assert_called_once_with()
        strf = dmock.now.return_value.strftime
        strf.assert_called_once_with("%a %x")
        buffers = [
            mock_call.kwargs["file"]
            for mock_call in prnt.call_args_list
        ]
        self.assertEqual(buffers, [ctx.output.stdout] * 2 + [sys.stderr])
        inp.assert_called_once_with()
        self.assertEqual(ctx.error_level, 1)
