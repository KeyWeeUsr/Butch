from unittest import main, TestCase
from unittest.mock import MagicMock, patch, call as mock_call


class BetterParser(TestCase):
    def test_read_line(self):
        from parser import read_line
        self.assertEqual(read_line("-\x1a-"), "-\n-")

    def test_read_file(self):
        from parser import read_file
        text = "one\x1atwo\nthree\x1a\nfour\n\x1afive\n"
        read = MagicMock()
        read.read.return_value = text

        enter = MagicMock()
        enter.__enter__.return_value = read
        with patch("builtins.open", return_value=enter) as opn:
            self.assertEqual(
                read_file("nonexisting"),
                ["one", "two", "three", "", "four", "", "five"]
            )
            opn.assert_called_once_with("nonexisting")
            enter.__enter__.assert_called_once_with()
            read.read.assert_called_once_with()

    def test_percent_expansion(self):
        from parser import percent_expansion as pxp
        from context import Context

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
        self.assertEqual(pxp(line="%%1hello%", ctx=ctx), f"%1hello")
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
        from tokenizer import tokenize
        from context import Context
        self.assertEqual(tokenize(text="\r", ctx=Context()), [])

    def test_carret_toggle_escape(self):
        from tokenizer import tokenize, Flag
        from context import Context
        flags = dict(tokenize(text="^", ctx=Context(), debug=True))
        self.assertTrue(flags[Flag.ESCAPE])

    def test_quote_double_toggle(self):
        from tokenizer import tokenize, Flag
        from context import Context
        flags = dict(tokenize(text='"', ctx=Context(), debug=True))
        self.assertTrue(flags[Flag.QUOTE])

    def test_quote_double_untoggle(self):
        from tokenizer import tokenize, Flag
        from context import Context
        flags = dict(tokenize(text='""', ctx=Context(), debug=True))
        self.assertFalse(flags[Flag.QUOTE])

    def test_lf_untoggle_quote(self):
        from tokenizer import tokenize, Flag
        from context import Context
        flags = dict(tokenize(text='"\n', ctx=Context(), debug=True))
        self.assertFalse(flags[Flag.QUOTE])

    def test_quote_flag_strip_escaped_lf(self):
        from tokenizer import tokenize, Flag
        from context import Context
        flags = dict(tokenize(text='"^\n', ctx=Context(), debug=True))
        self.assertFalse(flags[Flag.QUOTE])
        self.assertEqual(tokenize(text='"^\n', ctx=Context(), debug=False), [])

    def test_unknown(self):
        from tokenizer import tokenize, Command
        from commands import Command as CommandType
        from context import Context
        cmd = "-\n"

        output = tokenize(text=cmd, ctx=Context())
        self.assertIsInstance(output, list)
        self.assertEqual(len(output), 1)
        com = output[0]
        self.assertIsInstance(com, Command)
        self.assertEqual(com.cmd, CommandType.UNKNOWN)
        self.assertTrue(com.echo)

    def test_unknown_without_newline(self):
        from tokenizer import tokenize, Command
        from commands import Command as CommandType
        from context import Context
        cmd = "-"

        output = tokenize(text=cmd, ctx=Context())
        self.assertIsInstance(output, list)
        self.assertEqual(len(output), 1)
        com = output[0]
        self.assertIsInstance(com, Command)
        self.assertEqual(com.cmd, CommandType.UNKNOWN)
        self.assertTrue(com.echo)

    def test_echo(self):
        from tokenizer import tokenize, Command, Argument
        from commands import Command as CommandType
        from context import Context

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
        from tokenizer import tokenize, Command, Argument
        from commands import Command as CommandType
        from context import Context

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
        from tokenizer import tokenize, Command, Argument
        from commands import Command as CommandType
        from context import Context

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
        from tokenizer import tokenize, Command, Argument
        from commands import Command as CommandType
        from context import Context

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
        from tokenizer import tokenize, Command, Argument
        from commands import Command as CommandType
        from context import Context

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
        from tokenizer import tokenize, Command, Argument
        from commands import Command as CommandType
        from context import Context

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
        from tokenizer import tokenize, Command
        from commands import Command as CommandType
        from context import Context

        param = "hello"

        for cmd in ["", "\n", "\r\n"]:
            output = tokenize(text=cmd, ctx=Context())
            self.assertIsInstance(output, list)
            self.assertEqual(len(output), 0)

    def test_empty_without_newline(self):
        from tokenizer import tokenize, Command
        from commands import Command as CommandType
        from context import Context

        param = "hello"

        for cmd in ["", "\n", "\r\n"]:
            output = tokenize(text=cmd, ctx=Context())
            self.assertIsInstance(output, list)
            self.assertEqual(len(output), 0)

    def test_empty_multi(self):
        from tokenizer import tokenize, Command
        from commands import Command as CommandType
        from context import Context

        param = "hello"

        for cmd in ["", "\n", "\r\n"]:
            output = tokenize(text=cmd * 3, ctx=Context())
            self.assertIsInstance(output, list)
            self.assertEqual(len(output), 0)

    def test_empty_multi_without_newline(self):
        from tokenizer import tokenize, Command
        from commands import Command as CommandType
        from context import Context

        param = "hello"

        for cmd in ["", " ", "\r"]:
            output = tokenize(text=cmd * 3, ctx=Context())
            self.assertIsInstance(output, list)
            self.assertEqual(len(output), 0)


class Parser(TestCase):
    def test_unknown(self):
        from parser import parse
        from commands import Command
        cmd = "-"
        self.assertEqual(parse(cmd), (Command.UNKNOWN, [cmd]))

    def test_echo(self):
        from parser import parse
        from commands import Command
        params = ["hello"]
        cmd = f"echo {params[0]}"
        self.assertEqual(parse(cmd), (Command.ECHO, params))

    def test_cd(self):
        from parser import parse
        from commands import Command
        params = ["hello"]
        cmd = f"cd {params[0]}"
        self.assertEqual(parse(cmd), (Command.CD, params))

    def test_set(self):
        from parser import parse
        from commands import Command
        params = ["hello"]
        cmd = f"set {params[0]}"
        self.assertEqual(parse(cmd), (Command.SET, params))

    def test_empty(self):
        from parser import clear_input as clr
        for item in ["", "\n", "\r\n"]:
            self.assertFalse(bool(clr(item)))

    def test_empty_multi(self):
        from parser import clear_input as clr
        for item in ["", "\n", "\r\n"]:
            self.assertFalse(bool(clr(item * 3)))


class Caller(TestCase):
    def test_map_resolve(self):
        from caller import call
        from context import Context
        from commands import Command

        params = [str(val) for val in range(3)]

        ctx = Context()
        with patch("commands.echo") as echo:
            self.assertEqual(call(Command.ECHO, params=params, ctx=ctx), None)
            echo.assert_called_once_with(params=params, ctx=ctx)

    def test_map_resolve_new(self):
        from caller import new_call as call
        from context import Context
        from commands import Command as CommandType
        from tokenizer import Command, Argument

        params = [str(val) for val in range(3)]
        args = [Argument(value=value) for value in params]

        ctx = Context()
        with patch("commands.echo") as echo:
            self.assertEqual(call(cmd=Command(
                cmd=CommandType.ECHO,
                args=args
            ), ctx=ctx), None)
            echo.assert_called_once_with(params=args, ctx=ctx)

    def test_map_unresolved(self):
        from caller import call
        from commands import Command
        echo = MagicMock()
        params = [str(val) for val in range(3)]

        with self.assertRaises(Exception):
            call(Command.UNKNOWN, params)

    def test_map_unresolved_new(self):
        from caller import new_call as call
        from commands import Command as CommandType
        from tokenizer import Command, Argument
        echo = MagicMock()
        params = [str(val) for val in range(3)]

        with self.assertRaises(Exception):
            call(Command(cmd=CommandType.UNKNOWN, args=[
                Argument(value=value) for value in params
            ]))
                


class Context(TestCase):
    def test_unknown_skipped(self):
        from context import Context
        with self.assertRaises(Exception):
            Contest(unknown=123)

    def test_known_init(self):
        from context import Context
        from random import randint
        known = ["cwd"]
        kwargs = {item: randint(1,5) for item in known}
        ctx = Context(**kwargs)
        for key, val in kwargs.items():
            self.assertEqual(getattr(ctx, key), val)


class Execution(TestCase):
    def test_echo_new(self):
        import sys
        from commands import Command as CommandType
        from tokenizer import Command, Argument
        from caller import new_call as call
        from context import Context

        ctx = Context()
        values = ["a", "b", "c"]

        with patch("commands.print") as mock:
            call(cmd=Command(cmd=CommandType.ECHO, args=[
                Argument(value=value)
                for value in values
            ]), ctx=ctx)
            mock.assert_called_once_with(*values, file=sys.stdout)

        self.assertEqual(ctx.error_level, 0)

    def test_cd_nonexisting(self):
        import sys
        from commands import Command
        from caller import call
        from context import Context
        from constants import PATH_NOT_FOUND

        ctx = Context()
        args = {"params": ["nonexistingfile"], "ctx": ctx}

        chdir_mock = patch("os.chdir", side_effect=FileNotFoundError())
        with chdir_mock as chdir, patch("commands.print") as mock:
            call(Command.CD, **args)
            chdir.assert_called_once_with(args["params"][0])
            mock.assert_called_once_with(PATH_NOT_FOUND, file=sys.stdout)

        self.assertEqual(ctx.error_level, 1)

    def test_cd_nonexisting_new(self):
        import sys
        from commands import Command as CommandType
        from tokenizer import Command, Argument
        from caller import new_call as call
        from context import Context
        from constants import PATH_NOT_FOUND

        ctx = Context()
        value = "nonexistingfile"

        chdir_mock = patch("os.chdir", side_effect=FileNotFoundError())
        with chdir_mock as chdir, patch("commands.print") as mock:
            call(cmd=Command(cmd=CommandType.CD, args=[
                Argument(value=value)
            ]), ctx=ctx)
            chdir.assert_called_once_with(value)
            mock.assert_called_once_with(PATH_NOT_FOUND, file=sys.stdout)

        self.assertEqual(ctx.error_level, 1)

    def test_cd_existing(self):
        from commands import Command
        from caller import call
        from context import Context
        from constants import PATH_NOT_FOUND

        ctx = Context()
        args = {"params": ["existing"], "ctx": ctx}

        with patch("os.chdir") as chdir, patch("commands.print") as mock:
            call(Command.CD, **args)
            chdir.assert_called_once_with(args["params"][0])

        self.assertEqual(ctx.error_level, 0)

    def test_cd_existing_new(self):
        from commands import Command as CommandType
        from tokenizer import Command, Argument
        from caller import new_call as call
        from context import Context
        from constants import PATH_NOT_FOUND

        ctx = Context()
        value = "existing"

        with patch("os.chdir") as chdir, patch("commands.print") as mock:
            call(cmd=Command(cmd=CommandType.CD, args=[
                Argument(value=value)
            ]), ctx=ctx)
            chdir.assert_called_once_with(value)

        self.assertEqual(ctx.error_level, 0)

    def test_set_dumpall(self):
        from commands import Command
        from caller import call
        from context import Context

        ctx = Context()
        args = {"params": [], "ctx": ctx}

        with patch("commands._print_all_variables") as mock:
            call(Command.SET, **args)
            mock.assert_called_once_with(ctx=ctx)

        self.assertEqual(ctx.error_level, 0)

    def test_set_dumpall_new(self):
        from commands import Command as CommandType
        from tokenizer import Command, Argument
        from caller import new_call as call
        from context import Context

        ctx = Context()

        with patch("commands._print_all_variables") as mock:
            call(cmd=Command(cmd=CommandType.SET, args=[]), ctx=ctx)
            mock.assert_called_once_with(ctx=ctx)

        self.assertEqual(ctx.error_level, 0)

    def test_set_dumpsingle_new(self):
        from commands import Command as CommandType
        from tokenizer import Command, Argument
        from caller import new_call as call
        from context import Context

        ctx = Context()
        value = "hello"

        with patch("commands._print_single_variable") as mock:
            call(cmd=Command(cmd=CommandType.SET, args=[
                Argument(value=value)
            ]), ctx=ctx)
            mock.assert_called_once_with(key=value, ctx=ctx)

        self.assertEqual(ctx.error_level, 0)

    def test_set_unset_new(self):
        from commands import Command as CommandType
        from tokenizer import Command, Argument
        from caller import new_call as call
        from context import Context

        ctx = Context()
        value = "hello"

        with patch("commands._delete_single_variable") as mock:
            call(cmd=Command(cmd=CommandType.SET, args=[
                Argument(value=f"{value}=")
            ]), ctx=ctx)
            mock.assert_called_once_with(key=value, ctx=ctx)

        self.assertEqual(ctx.error_level, 0)

    def test_set_setsingle_new(self):
        from commands import Command as CommandType
        from tokenizer import Command, Argument
        from caller import new_call as call
        from context import Context

        ctx = Context()
        value = "123"
        key = "hello"

        with patch("context.Context.set_variable") as mock:
            call(cmd=Command(cmd=CommandType.SET, args=[
                Argument(value=f"{key}={value}")
            ]), ctx=ctx)
            mock.assert_called_once_with(key=key, value=value)

        self.assertEqual(ctx.error_level, 0)


class BatchFiles(TestCase):
    def test_hello_new(self):
        import sys
        from os.path import join, dirname, abspath

        script_name = "hello.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle_new

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context()
            handle_new(text=join(folder, script_name), ctx=ctx)
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(*out.rstrip("\n").split(" "), file=sys.stdout)
                )

    def test_cd_existing_new(self):
        import sys
        from os.path import join, dirname, abspath

        script_name = "cd_existing.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle_new

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("os.chdir") as cdr, patch("builtins.print") as stdout:
            ctx = Context()
            handle_new(text=join(folder, script_name), ctx=ctx)
            cdr.assert_called_once_with("..")
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(*out.rstrip("\n").split(" "), file=sys.stdout)
                )

    def test_cd_nonexisting_new(self):
        import sys
        from os.path import join, dirname, abspath

        script_name = "cd_nonexisting.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle_new

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context()
            handle_new(text=join(folder, script_name), ctx=ctx)
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(out.rstrip("\n"), file=sys.stdout)
                )

    def test_set_join_new(self):
        import sys
        from os.path import join, dirname, abspath

        script_name = "set_join.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle_new

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context()
            handle_new(text=join(folder, script_name), ctx=ctx)
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(out.rstrip("\n"), file=sys.stdout)
                )

    def test_echo_quote(self):
        import sys
        from os.path import join, dirname, abspath

        script_name = "hello_quote.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle_new

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context(history_enabled=False)
            handle_new(text=join(folder, script_name), ctx=ctx)
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            ctx.log.debug("->, %s", stdout.mock_calls)
            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(out.rstrip("\n"), file=sys.stdout)
                )

    def test_set_quote(self):
        import sys
        from os.path import join, dirname, abspath

        script_name = "set_quote.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle_new

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context(history_enabled=False)
            handle_new(text=join(folder, script_name), ctx=ctx)
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(out.rstrip("\n"), file=sys.stdout)
                )

    def test_set_quote_2(self):
        import sys
        from os.path import join, dirname, abspath

        script_name = "set_quote_2.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle_new

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context(history_enabled=False)
            handle_new(text=join(folder, script_name), ctx=ctx)
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(out.rstrip("\n"), file=sys.stdout)
                )

    def test_set_quote_3(self):
        import sys
        from os.path import join, dirname, abspath

        script_name = "set_quote_3.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle_new

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context(history_enabled=False)
            handle_new(text=join(folder, script_name), ctx=ctx)
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(out.rstrip("\n"), file=sys.stdout)
                )

    def test_set_quote_4(self):
        import sys
        from os.path import join, dirname, abspath

        script_name = "set_quote_4.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle_new

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context(history_enabled=False)
            handle_new(text=join(folder, script_name), ctx=ctx)
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(out.rstrip("\n"), file=sys.stdout)
                )

    def test_set_quote_5(self):
        import sys
        from os.path import join, dirname, abspath

        script_name = "set_quote_5.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle_new

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context(history_enabled=False)
            handle_new(text=join(folder, script_name), ctx=ctx)
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(out.rstrip("\n"), file=sys.stdout)
                )

    def test_set_quote_6(self):
        import sys
        from os.path import join, dirname, abspath

        script_name = "set_quote_6.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle_new

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context(history_enabled=False)
            handle_new(text=join(folder, script_name), ctx=ctx)
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(out.rstrip("\n"), file=sys.stdout)
                )

    def test_set_quote_7(self):
        import sys
        from os.path import join, dirname, abspath

        script_name = "set_quote_7.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle_new

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context(history_enabled=False)
            handle_new(text=join(folder, script_name), ctx=ctx)
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(out.rstrip("\n"), file=sys.stdout)
                )

    def test_delete_file(self):
        import sys
        from os import remove
        from os.path import join, dirname, abspath, exists

        script_name = "delete_file.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle_new

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context(history_enabled=False)
            tmp = script_name.replace(".bat", ".tmp")

            if exists(tmp):
                remove(tmp)
            with open(tmp, "w") as file:
                file.write(".")
            self.assertTrue(exists(tmp))

            handle_new(text=join(folder, script_name), ctx=ctx)
            self.assertFalse(exists(tmp))

            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(out.rstrip("\n"), file=sys.stdout)
                )

    def test_delete_file_syntax(self):
        from os.path import join, dirname, abspath, exists

        script_name = "delete_file_syntax.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle_new

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context(history_enabled=False)
            handle_new(text=join(folder, script_name), ctx=ctx)

            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(out.rstrip("\n"))
                )


    def test_delete_folder_pipe(self):
        import sys
        from os import mkdir, rmdir, listdir
        from shutil import rmtree
        from os.path import join, dirname, abspath, exists

        script_name = "delete_folder_files.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')
        tmp_folder = join("/tmp", "butch-tmp")

        from context import Context
        from constants import SURE
        from main import handle_new

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

    def ignore_test_set_join_expansion(self):
        from os.path import join, dirname, abspath

        script_name = "set_join_expansion.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context()
            handle(text=join(folder, script_name), ctx=ctx)
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
