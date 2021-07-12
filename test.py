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

    def test_map_unresolved(self):
        from caller import call
        from commands import Command
        echo = MagicMock()
        params = [str(val) for val in range(3)]

        with self.assertRaises(Exception):
            call(Command.UNKNOWN, params)


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
    def test_echo(self):
        from commands import Command
        from caller import call
        from context import Context

        ctx = Context()
        args = {"params": ["a", "b", "c"], "ctx": ctx}

        with patch("commands.print") as mock:
            call(Command.ECHO, **args)
            mock.assert_called_once_with(*args["params"])

        self.assertEqual(ctx.error_level, 0)

    def test_cd_nonexisting(self):
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
            mock.assert_called_once_with(PATH_NOT_FOUND)

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

    def test_set_dumpsingle(self):
        from commands import Command
        from caller import call
        from context import Context

        ctx = Context()
        key = "hello"
        args = {"params": [key], "ctx": ctx}

        with patch("commands._print_single_variable") as mock:
            call(Command.SET, **args)
            mock.assert_called_once_with(key=key, ctx=ctx)

        self.assertEqual(ctx.error_level, 0)

    def test_set_unset(self):
        from commands import Command
        from caller import call
        from context import Context

        ctx = Context()
        key = "hello"
        args = {"params": [f"{key}="], "ctx": ctx}

        with patch("commands._delete_single_variable") as mock:
            call(Command.SET, **args)
            mock.assert_called_once_with(key=key, ctx=ctx)

        self.assertEqual(ctx.error_level, 0)

    def test_set_setsingle(self):
        from commands import Command
        from caller import call
        from context import Context

        ctx = Context()
        value = "123"
        key = "hello"
        args = {"params": [f"{key}={value}"], "ctx": ctx}

        with patch("context.Context.set_variable") as mock:
            call(Command.SET, **args)
            mock.assert_called_once_with(key=key, value=value)

        self.assertEqual(ctx.error_level, 0)


class BatchFiles(TestCase):
    def test_hello(self):
        from os.path import join, dirname, abspath

        script_name = "hello.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context()
            handle(text=join(folder, script_name), ctx=ctx)
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(*out.rstrip("\n").split(" "))
                )

    def test_cd_existing(self):
        from os.path import join, dirname, abspath

        script_name = "cd_existing.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("os.chdir") as cdr, patch("builtins.print") as stdout:
            ctx = Context()
            handle(text=join(folder, script_name), ctx=ctx)
            cdr.assert_called_once_with("..")
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(*out.rstrip("\n").split(" "))
                )

    def test_cd_nonexisting(self):
        from os.path import join, dirname, abspath

        script_name = "cd_nonexisting.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context()
            handle(text=join(folder, script_name), ctx=ctx)
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(out.rstrip("\n"))
                )

    def test_set_join(self):
        from os.path import join, dirname, abspath

        script_name = "set_join.bat"
        out_name = f"{script_name}.out"
        folder = join(dirname(abspath(__file__)), 'batch')

        from context import Context
        from main import handle

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context()
            handle(text=join(folder, script_name), ctx=ctx)
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(out.rstrip("\n"))
                )

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
