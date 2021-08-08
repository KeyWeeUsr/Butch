# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

import sys
from io import StringIO
from typing import Callable
from unittest import main, TestCase
from unittest.mock import patch, call as mock_call, _CallList, MagicMock
from os.path import join, dirname, abspath, exists


class BetterParser(TestCase):
    def test_percent_expansion(self):
        from butch.expansion import percent_expansion as pxp
        from butch.context import Context

        ctx = Context()
        ctx.set_variable("hello", "value")
        self.assertEqual(pxp(line="abc", ctx=ctx), "abc")
        self.assertEqual(pxp(line="%", ctx=ctx), "")

        arg_one = "one"
        arg_two = "two"
        arg_three = "three"
        arg_all = [arg_one, arg_two, arg_three]
        with patch("sys.argv", ["-", *arg_all]):
            self.assertEqual(pxp(line="%1", ctx=ctx), arg_one)
            self.assertEqual(pxp(line="%2", ctx=ctx), arg_two)
            self.assertEqual(pxp(line="%3", ctx=ctx), arg_three)
            self.assertEqual(pxp(line="%1%2%3", ctx=ctx), "".join(arg_all))
            self.assertEqual(pxp(line="%*", ctx=ctx), " ".join(arg_all))
            self.assertEqual(pxp(line="%1hello%", ctx=ctx), f"{arg_one}hello")
            self.assertEqual(pxp(line="%1hello%", ctx=ctx), f"{arg_one}hello")
        self.assertEqual(pxp(line="%%1hello%", ctx=ctx), "%1hello")
        self.assertEqual(pxp(line="%", ctx=ctx), "")
        self.assertEqual(pxp(line="%%", ctx=ctx), "%")
        self.assertEqual(pxp(line="%%%", ctx=ctx), "%")
        self.assertEqual(pxp(line="%%%%", ctx=ctx), "%%")
        self.assertEqual(pxp(line="%%%%%", ctx=ctx), "%%")
        self.assertEqual(pxp(line="%hello%", ctx=ctx), "value")
        self.assertEqual(pxp(line="%%hello%", ctx=ctx), "%hello")
        self.assertEqual(pxp(line="%hello%%", ctx=ctx), "value")
        self.assertEqual(pxp(line="%%hello%%", ctx=ctx), "%hello%")
        self.assertEqual(pxp(line="-%hello%-", ctx=ctx), "-value-")
        self.assertEqual(pxp(line="-%%hello%-", ctx=ctx), "-%hello-")
        self.assertEqual(pxp(line="-%hello%%-", ctx=ctx), "-value-")
        self.assertEqual(pxp(line="-%%hello%%-", ctx=ctx), "-%hello%-")


class Tokenizer(TestCase):
    def test_remove_carriage_return(self):
        from butch.tokenizer import tokenize
        from butch.context import Context
        self.assertEqual(tokenize(text="\r", ctx=Context()), [])

    def test_carret_toggle_escape(self):
        from butch.tokenizer import tokenize, Flag
        from butch.context import Context
        flags = dict(tokenize(text="^", ctx=Context(), debug=True))
        self.assertTrue(flags[Flag.ESCAPE])

    def test_quote_double_toggle(self):
        from butch.tokenizer import tokenize, Flag
        from butch.context import Context
        flags = dict(tokenize(text='"', ctx=Context(), debug=True))
        self.assertTrue(flags[Flag.QUOTE])

    def test_quote_double_untoggle(self):
        from butch.tokenizer import tokenize, Flag
        from butch.context import Context
        flags = dict(tokenize(text='""', ctx=Context(), debug=True))
        self.assertFalse(flags[Flag.QUOTE])

    def test_lf_untoggle_quote(self):
        from butch.tokenizer import tokenize, Flag
        from butch.context import Context
        flags = dict(tokenize(text='"\n', ctx=Context(), debug=True))
        self.assertFalse(flags[Flag.QUOTE])

    def test_quote_flag_strip_escaped_lf(self):
        from butch.tokenizer import tokenize, Flag
        from butch.context import Context
        flags = dict(tokenize(text='"^\n', ctx=Context(), debug=True))
        self.assertFalse(flags[Flag.QUOTE])
        self.assertEqual(tokenize(text='"^\n', ctx=Context(), debug=False), [])

    def test_unknown(self):
        from butch.tokenizer import tokenize, Command
        from butch.commandtype import CommandType
        from butch.context import Context
        cmd = "-\n"

        output = tokenize(text=cmd, ctx=Context())
        self.assertIsInstance(output, list)
        self.assertEqual(len(output), 1)
        com = output[0]
        self.assertIsInstance(com, Command)
        self.assertEqual(com.cmd, CommandType.UNKNOWN)
        self.assertTrue(com.echo)

    def test_unknown_without_newline(self):
        from butch.tokenizer import tokenize, Command
        from butch.commandtype import CommandType
        from butch.context import Context
        cmd = "-"

        output = tokenize(text=cmd, ctx=Context())
        self.assertIsInstance(output, list)
        self.assertEqual(len(output), 1)
        com = output[0]
        self.assertIsInstance(com, Command)
        self.assertEqual(com.cmd, CommandType.UNKNOWN)
        self.assertTrue(com.echo)

    def test_echo(self):
        from butch.tokenizer import tokenize, Command, Argument
        from butch.commandtype import CommandType
        from butch.context import Context

        param = "hello"
        cmd = f"echo {param}\n"

        output = tokenize(text=cmd, ctx=Context())
        self.assertIsInstance(output, list)
        self.assertEqual(len(output), 1)
        com = output[0]
        self.assertIsInstance(com, Command)
        self.assertEqual(com.cmd, CommandType.ECHO)
        self.assertTrue(com.echo)
        self.assertEqual(com.args, [Argument(value=param)])

    def test_echo_without_newline(self):
        from butch.tokenizer import tokenize, Command, Argument
        from butch.commandtype import CommandType
        from butch.context import Context

        param = "hello"
        cmd = f"echo {param}"

        output = tokenize(text=cmd, ctx=Context())
        self.assertIsInstance(output, list)
        self.assertEqual(len(output), 1)
        com = output[0]
        self.assertIsInstance(com, Command)
        self.assertEqual(com.cmd, CommandType.ECHO)
        self.assertTrue(com.echo)
        self.assertEqual(com.args, [Argument(value=param)])

    def test_cd(self):
        from butch.tokenizer import tokenize, Command, Argument
        from butch.commandtype import CommandType
        from butch.context import Context

        param = "hello"
        cmd = f"cd {param}\n"

        output = tokenize(text=cmd, ctx=Context())
        self.assertIsInstance(output, list)
        self.assertEqual(len(output), 1)
        com = output[0]
        self.assertIsInstance(com, Command)
        self.assertEqual(com.cmd, CommandType.CD)
        self.assertTrue(com.echo)
        self.assertEqual(com.args, [Argument(value=param)])

    def test_cd_without_newline(self):
        from butch.tokenizer import tokenize, Command, Argument
        from butch.commandtype import CommandType
        from butch.context import Context

        param = "hello"
        cmd = f"cd {param}"

        output = tokenize(text=cmd, ctx=Context())
        self.assertIsInstance(output, list)
        self.assertEqual(len(output), 1)
        com = output[0]
        self.assertIsInstance(com, Command)
        self.assertEqual(com.cmd, CommandType.CD)
        self.assertTrue(com.echo)
        self.assertEqual(com.args, [Argument(value=param)])

    def test_set(self):
        from butch.tokenizer import tokenize, Command, Argument
        from butch.commandtype import CommandType
        from butch.context import Context

        param = "hello"
        cmd = f"set {param}\n"

        output = tokenize(text=cmd, ctx=Context())
        self.assertIsInstance(output, list)
        self.assertEqual(len(output), 1)
        com = output[0]
        self.assertIsInstance(com, Command)
        self.assertEqual(com.cmd, CommandType.SET)
        self.assertTrue(com.echo)
        self.assertEqual(com.args, [Argument(value=param)])

    def test_set_without_newline(self):
        from butch.tokenizer import tokenize, Command, Argument
        from butch.commandtype import CommandType
        from butch.context import Context

        param = "hello"
        cmd = f"set {param}"

        output = tokenize(text=cmd, ctx=Context())
        self.assertIsInstance(output, list)
        self.assertEqual(len(output), 1)
        com = output[0]
        self.assertIsInstance(com, Command)
        self.assertEqual(com.cmd, CommandType.SET)
        self.assertTrue(com.echo)
        self.assertEqual(com.args, [Argument(value=param)])

    def test_empty(self):
        from butch.tokenizer import tokenize
        from butch.context import Context

        for cmd in ["", "\n", "\r\n"]:
            output = tokenize(text=cmd, ctx=Context())
            self.assertIsInstance(output, list)
            self.assertEqual(len(output), 0)

    def test_empty_without_newline(self):
        from butch.tokenizer import tokenize
        from butch.context import Context

        for cmd in ["", "\n", "\r\n"]:
            output = tokenize(text=cmd, ctx=Context())
            self.assertIsInstance(output, list)
            self.assertEqual(len(output), 0)

    def test_empty_multi(self):
        from butch.tokenizer import tokenize
        from butch.context import Context

        for cmd in ["", "\n", "\r\n"]:
            output = tokenize(text=cmd * 3, ctx=Context())
            self.assertIsInstance(output, list)
            self.assertEqual(len(output), 0)

    def test_empty_multi_without_newline(self):
        from butch.tokenizer import tokenize
        from butch.context import Context

        for cmd in ["", " ", "\r"]:
            output = tokenize(text=cmd * 3, ctx=Context())
            self.assertIsInstance(output, list)
            self.assertEqual(len(output), 0)


class State(TestCase):
    def test_unknown_skipped(self):
        from butch.context import Context
        with self.assertRaises(Exception):
            Context(unknown=123)

    def test_known_init(self):
        from butch.context import Context
        from random import randint
        known = ["cwd"]
        kwargs = {item: randint(1, 5) for item in known}
        ctx = Context(**kwargs)
        for key, val in kwargs.items():
            self.assertEqual(getattr(ctx, key), val)


class Execution(TestCase):
    def test_echo_new(self):
        from butch.commandtype import CommandType
        from butch.tokenizer import Command, Argument
        from butch.caller import new_call as call
        from butch.context import Context

        ctx = Context()
        values = ["a", "b", "c"]

        with patch("butch.commands.print") as mock:
            call(cmd=Command(cmd=CommandType.ECHO, args=[
                Argument(value=value)
                for value in values
            ]), ctx=ctx)
            mock.assert_called_once_with(*values, file=sys.stdout)

        self.assertEqual(ctx.error_level, 0)

    def test_cd_nonexisting_new(self):
        from butch.commandtype import CommandType
        from butch.tokenizer import Command, Argument
        from butch.caller import new_call as call
        from butch.context import Context
        from butch.constants import PATH_NOT_FOUND

        ctx = Context()
        value = "nonexistingfile"

        chdir_mock = patch(
            "butch.context.chdir", side_effect=FileNotFoundError()
        )
        with chdir_mock as chdir, patch("butch.commands.print") as mock:
            call(cmd=Command(cmd=CommandType.CD, args=[
                Argument(value=value)
            ]), ctx=ctx)
            chdir.assert_called_once_with(value)
            mock.assert_called_once_with(PATH_NOT_FOUND, file=sys.stderr)

        self.assertEqual(ctx.error_level, 1)

    def test_cd_existing_new(self):
        from butch.commandtype import CommandType
        from butch.tokenizer import Command, Argument
        from butch.caller import new_call as call
        from butch.context import Context

        ctx = Context()
        value = "existing"

        chdir_mock = patch("butch.context.chdir")
        with chdir_mock as chdir, patch("butch.commands.print") as mock:
            call(cmd=Command(cmd=CommandType.CD, args=[
                Argument(value=value)
            ]), ctx=ctx)
            chdir.assert_called_once_with(value)
            mock.assert_not_called()

        self.assertEqual(ctx.error_level, 0)

    def test_set_dumpall_new(self):
        from butch.commandtype import CommandType
        from butch.tokenizer import Command
        from butch.caller import new_call as call
        from butch.context import Context

        ctx = Context()

        with patch("butch.commands._print_all_variables") as mock:
            call(cmd=Command(cmd=CommandType.SET, args=[]), ctx=ctx)
            mock.assert_called_once_with(ctx=ctx, file=sys.stdout)

        self.assertEqual(ctx.error_level, 0)

    def test_set_dumpsingle_new(self):
        from butch.commandtype import CommandType
        from butch.tokenizer import Command, Argument
        from butch.caller import new_call as call
        from butch.context import Context

        ctx = Context()
        value = "hello"

        with patch("butch.commands._print_single_variable") as mock:
            call(cmd=Command(cmd=CommandType.SET, args=[
                Argument(value=value)
            ]), ctx=ctx)
            mock.assert_called_once_with(key=value, ctx=ctx, file=sys.stdout)

        self.assertEqual(ctx.error_level, 0)

    def test_set_unset_new(self):
        from butch.commandtype import CommandType
        from butch.tokenizer import Command, Argument
        from butch.caller import new_call as call
        from butch.context import Context

        ctx = Context()
        value = "hello"

        ctx.delete_variable = MagicMock()
        call(cmd=Command(cmd=CommandType.SET, args=[
            Argument(value=f"{value}=")
        ]), ctx=ctx)
        ctx.delete_variable.assert_called_once_with(key=value)
        self.assertEqual(ctx.error_level, 0)

    def test_set_setsingle_new(self):
        from butch.commandtype import CommandType
        from butch.tokenizer import Command, Argument
        from butch.caller import new_call as call
        from butch.context import Context

        ctx = Context()
        value = "123"
        key = "hello"

        with patch("butch.context.Context.set_variable") as mock:
            call(cmd=Command(cmd=CommandType.SET, args=[
                Argument(value=f"{key}={value}")
            ]), ctx=ctx)
            mock.assert_called_once_with(key=key, value_to_set=value)

        self.assertEqual(ctx.error_level, 0)


if __name__ == "__main__":
    main()
