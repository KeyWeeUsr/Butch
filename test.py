from unittest import main, TestCase
from unittest.mock import MagicMock


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
        from commands import Command, CMD_MAP
        echo = MagicMock()
        CMD_MAP[Command.ECHO] = echo
        params = [str(val) for val in range(3)]

        self.assertEqual(call(Command.ECHO, params), None)
        echo.assert_called_once_with(params)

    def test_map_unresolved(self):
        from caller import call
        from commands import Command, CMD_MAP
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


if __name__ == "__main__":
    main()
