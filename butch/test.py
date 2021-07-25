# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

import sys
from io import StringIO
from typing import Callable
from unittest import main, TestCase
from unittest.mock import patch, call as mock_call, _CallList
from os.path import join, dirname, abspath, exists
BATCH_FOLDER = join(dirname(abspath(__file__)), "batch")


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
        from butch.commands import Command as CommandType
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
        from butch.commands import Command as CommandType
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
        from butch.commands import Command as CommandType
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
        from butch.commands import Command as CommandType
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
        from butch.commands import Command as CommandType
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
        from butch.commands import Command as CommandType
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
        from butch.commands import Command as CommandType
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
        from butch.commands import Command as CommandType
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


class Parser(TestCase):
    def test_unknown(self):
        from butch.commands import Command, parse
        cmd = "-"
        self.assertEqual(parse(cmd), (Command.UNKNOWN, [cmd]))

    def test_echo(self):
        from butch.commands import Command, parse
        params = ["hello"]
        cmd = f"echo {params[0]}"
        self.assertEqual(parse(cmd), (Command.ECHO, params))

    def test_cd(self):
        from butch.commands import Command, parse
        params = ["hello"]
        cmd = f"cd {params[0]}"
        self.assertEqual(parse(cmd), (Command.CD, params))

    def test_set(self):
        from butch.commands import Command, parse
        params = ["hello"]
        cmd = f"set {params[0]}"
        self.assertEqual(parse(cmd), (Command.SET, params))


class Caller(TestCase):
    def test_map_resolve_new(self):
        from butch.caller import new_call as call
        from butch.context import Context
        from butch.commands import Command as CommandType
        from butch.tokenizer import Command, Argument

        params = [str(val) for val in range(3)]
        args = [Argument(value=value) for value in params]

        ctx = Context()
        with patch("butch.commands.echo") as echo:
            self.assertEqual(call(cmd=Command(
                cmd=CommandType.ECHO,
                args=args
            ), ctx=ctx), None)
            echo.assert_called_once_with(params=args, ctx=ctx)

    def test_map_unresolved_new(self):
        from butch.caller import new_call, UnknownCommand
        from butch.commands import Command as CommandType
        from butch.tokenizer import Command, Argument
        from butch.context import Context
        params = [str(val) for val in range(3)]

        with self.assertRaises(UnknownCommand):
            new_call(Command(cmd=CommandType.UNKNOWN, args=[
                Argument(value=value) for value in params
            ]), ctx=Context())


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
        import sys
        from butch.commands import Command as CommandType
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
        import sys
        from butch.commands import Command as CommandType
        from butch.tokenizer import Command, Argument
        from butch.caller import new_call as call
        from butch.context import Context
        from butch.constants import PATH_NOT_FOUND

        ctx = Context()
        value = "nonexistingfile"

        chdir_mock = patch(
            "butch.commands.chdir", side_effect=FileNotFoundError()
        )
        with chdir_mock as chdir, patch("butch.commands.print") as mock:
            call(cmd=Command(cmd=CommandType.CD, args=[
                Argument(value=value)
            ]), ctx=ctx)
            chdir.assert_called_once_with(value)
            mock.assert_called_once_with(PATH_NOT_FOUND, file=sys.stdout)

        self.assertEqual(ctx.error_level, 1)

    def test_cd_existing_new(self):
        from butch.commands import Command as CommandType
        from butch.tokenizer import Command, Argument
        from butch.caller import new_call as call
        from butch.context import Context

        ctx = Context()
        value = "existing"

        chdir_mock = patch("butch.commands.chdir")
        with chdir_mock as chdir, patch("butch.commands.print") as mock:
            call(cmd=Command(cmd=CommandType.CD, args=[
                Argument(value=value)
            ]), ctx=ctx)
            chdir.assert_called_once_with(value)
            mock.assert_not_called()

        self.assertEqual(ctx.error_level, 0)

    def test_set_dumpall_new(self):
        from butch.commands import Command as CommandType
        from butch.tokenizer import Command
        from butch.caller import new_call as call
        from butch.context import Context

        ctx = Context()

        with patch("butch.commands._print_all_variables") as mock:
            call(cmd=Command(cmd=CommandType.SET, args=[]), ctx=ctx)
            mock.assert_called_once_with(ctx=ctx)

        self.assertEqual(ctx.error_level, 0)

    def test_set_dumpsingle_new(self):
        from butch.commands import Command as CommandType
        from butch.tokenizer import Command, Argument
        from butch.caller import new_call as call
        from butch.context import Context

        ctx = Context()
        value = "hello"

        with patch("butch.commands._print_single_variable") as mock:
            call(cmd=Command(cmd=CommandType.SET, args=[
                Argument(value=value)
            ]), ctx=ctx)
            mock.assert_called_once_with(key=value, ctx=ctx)

        self.assertEqual(ctx.error_level, 0)

    def test_set_unset_new(self):
        from butch.commands import Command as CommandType
        from butch.tokenizer import Command, Argument
        from butch.caller import new_call as call
        from butch.context import Context

        ctx = Context()
        value = "hello"

        with patch("butch.commands._delete_single_variable") as mock:
            call(cmd=Command(cmd=CommandType.SET, args=[
                Argument(value=f"{value}=")
            ]), ctx=ctx)
            mock.assert_called_once_with(key=value, ctx=ctx)

        self.assertEqual(ctx.error_level, 0)

    def test_set_setsingle_new(self):
        from butch.commands import Command as CommandType
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


def default_output_splitter(text: str) -> list:
    return text.rstrip("\n").split(" ")


def assert_bat_output_match(
        batch_path: str, mock_calls: _CallList,
        splitter: Callable = default_output_splitter,
        concat: bool = False, file_buff: StringIO = None
) -> bool:
    with open(join(BATCH_FOLDER, f"{batch_path}.out")) as file:
        output = file.readlines()
    assert len(mock_calls) == len(output), (mock_calls, output)

    pipe_text = "<pipe> "
    for idx, out in enumerate(output):
        buff = sys.stdout
        if out.startswith(pipe_text):
            out = out[len(pipe_text):]
            buff = file_buff
        text = splitter(out)

        left = mock_calls[idx]
        if concat:
            right = mock_call(" ".join(text), file=buff)
        else:
            right = mock_call(*text, file=buff)
        assert left == right, (left, right)


class BatchFiles(TestCase):
    @patch("builtins.print")
    def test_hello_new(self, stdout):
        script_name = "hello.bat"

        from butch.context import Context
        from butch.__main__ import handle_new

        ctx = Context()
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls)
        self.assertEqual(ctx.error_level, 0)

    @patch("builtins.print")
    def test_cd_existing_new(self, stdout):
        script_name = "cd_existing.bat"

        from butch.context import Context
        from butch.__main__ import handle_new

        with patch("butch.commands.chdir") as cdr:
            ctx = Context()
            handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
            cdr.assert_called_once_with("..")
            assert_bat_output_match(script_name, stdout.mock_calls)
            self.assertEqual(ctx.error_level, 0)

    @patch("builtins.print")
    def test_cd_nonexisting_new(self, stdout):
        script_name = "cd_nonexisting.bat"

        from butch.context import Context
        from butch.__main__ import handle_new

        with patch("builtins.print") as stdout:
            ctx = Context()
            handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
            assert_bat_output_match(
                script_name, stdout.mock_calls,
                concat=True
            )
            self.assertEqual(ctx.error_level, 1)

    @patch("builtins.print")
    def test_set_join_new(self, stdout):
        script_name = "set_join.bat"

        from butch.context import Context
        from butch.__main__ import handle_new

        ctx = Context()
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls)
        self.assertEqual(ctx.error_level, 0)

    @patch("builtins.print")
    def test_echo_quote(self, stdout):
        script_name = "hello_quote.bat"

        from butch.context import Context
        from butch.__main__ import handle_new

        ctx = Context(history_enabled=False)
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)
        self.assertEqual(ctx.error_level, 0)

    @patch("builtins.print")
    def test_set_quote(self, stdout):
        script_name = "set_quote.bat"

        from butch.context import Context
        from butch.__main__ import handle_new

        ctx = Context(history_enabled=False)
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @patch("builtins.print")
    def test_set_quote_2(self, stdout):
        script_name = "set_quote_2.bat"

        from butch.context import Context
        from butch.__main__ import handle_new

        ctx = Context(history_enabled=False)
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @patch("builtins.print")
    def test_set_quote_3(self, stdout):
        script_name = "set_quote_3.bat"

        from butch.context import Context
        from butch.__main__ import handle_new

        ctx = Context(history_enabled=False)
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @patch("builtins.print")
    def test_set_quote_4(self, stdout):
        script_name = "set_quote_4.bat"

        from butch.context import Context
        from butch.__main__ import handle_new

        ctx = Context(history_enabled=False)
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @patch("builtins.print")
    def test_set_quote_5(self, stdout):
        script_name = "set_quote_5.bat"

        from butch.context import Context
        from butch.__main__ import handle_new

        ctx = Context(history_enabled=False)
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @patch("builtins.print")
    def test_set_quote_6(self, stdout):
        script_name = "set_quote_6.bat"

        from butch.context import Context
        from butch.__main__ import handle_new

        ctx = Context(history_enabled=False)
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @patch("builtins.print")
    def test_set_quote_7(self, stdout):
        script_name = "set_quote_7.bat"

        from butch.context import Context
        from butch.__main__ import handle_new

        ctx = Context(history_enabled=False)
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @patch("builtins.print")
    def test_delete_file(self, stdout):
        from os import remove

        script_name = "delete_file.bat"

        from butch.context import Context
        from butch.__main__ import handle_new

        ctx = Context(history_enabled=False)
        tmp = script_name.replace(".bat", ".tmp")

        if exists(tmp):
            remove(tmp)
        with open(tmp, "w") as file:
            file.write(".")

        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        self.assertFalse(exists(tmp))
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @patch("builtins.print")
    def test_delete_file_syntax(self, stdout):
        script_name = "delete_file_syntax.bat"

        from butch.context import Context
        from butch.__main__ import handle_new

        ctx = Context(history_enabled=False)
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    def test_delete_folder_pipe(self):
        from os import mkdir, rmdir, listdir
        from shutil import rmtree

        script_name = "delete_folder_files.bat"
        out_name = f"{script_name}.out"
        folder = BATCH_FOLDER
        tmp_folder = join("/tmp", "butch-tmp")

        from butch.context import Context
        from butch.constants import SURE
        from butch.__main__ import handle_new

        with open(join(folder, script_name)) as file:
            script = file.readlines()
        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout, patch("os.remove") as rmv:
            ctx = Context(history_enabled=True)

            if exists(tmp_folder):
                rmtree(tmp_folder)

            mkdir(tmp_folder)

            handle_new(text=join(folder, script_name), ctx=ctx)
            rmv.assert_not_called()  # captured STDOUT prevents the call

            mcalls = stdout.mock_calls
            self.assertEqual(len(output), 2)
            self.assertEqual(len(mcalls), 3)

            self.assertTrue("|" in script[0])
            self.assertEqual(mcalls[0].args[0], output[0].rstrip("\n")[-1])
            self.assertEqual(str(ctx.error_level), output[1].rstrip("\n"))

            tmp = ctx.history[0].right.args[0].value.replace("/", "\\")
            self.assertEqual(mcalls[1].args[0], f"{tmp}\\*, {SURE} ")
            self.assertEqual(mcalls[2].args[0], str(ctx.error_level))

            self.assertTrue(exists(tmp_folder))
            self.assertEqual(listdir(tmp_folder), [])
            rmdir(tmp_folder)

    @patch("builtins.print")
    def test_mkdir_nonexisting(self, stdout):
        script_name = "mkdir_nonexisting.bat"

        from butch.context import Context
        from butch.__main__ import handle_new

        with patch("butch.commands.makedirs") as mdrs:
            ctx = Context()

            self.assertFalse(exists("new-folder"))
            handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)

            mdrs.assert_called_once()
            self.assertFalse(exists("new-folder"))
            assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @patch("builtins.print")
    def test_mkdir_tree(self, stdout):
        script_name = "mkdir_tree.bat"

        from butch.context import Context
        from butch.__main__ import handle_new

        tree = join("new-folder", "with", "sub", "folders")
        with patch("butch.commands.makedirs") as mdrs:
            ctx = Context()

            self.assertFalse(exists(tree))
            handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)

            mdrs.assert_called_once()
            self.assertFalse(exists(tree))
            assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @patch("builtins.print")
    def test_redir_newfile(self, stdout):
        from os import remove

        script_name = "redir_echo_newfile.bat"

        from butch.context import Context
        from butch.outputs import CommandOutput
        from butch.__main__ import handle_new

        filename = "new-file.txt"
        ctx = Context()

        if exists(filename):
            remove(filename)
        self.assertFalse(exists(filename))

        cmd_out = CommandOutput()
        with patch("butch.commands.CommandOutput") as out_mock:
            out_mock.return_value = cmd_out

            handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
            self.assertTrue(exists(filename))
            remove(filename)

            assert_bat_output_match(
                script_name, stdout.mock_calls, concat=True,
                file_buff=cmd_out.stdout
            )

    def ignore_test_set_join_expansion(self):
        script_name = "set_join_expansion.bat"
        out_name = f"{script_name}.out"
        folder = BATCH_FOLDER

        from butch.context import Context
        from butch.__main__ import handle_new

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context()
            handle_new(text=join(folder, script_name), ctx=ctx)
            self.assertTrue(ctx.delayed_expansion_enabled)
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(out.rstrip("\n"))
                )


if __name__ == "__main__":
    main()
