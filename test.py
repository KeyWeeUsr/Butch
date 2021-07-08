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


class Caller(TestCase):
    def test_map_resolve(self):
        from caller import call
        from commands import Command, CMD_MAP
        echo = MagicMock()
        CMD_MAP[Command.ECHO] = echo
        params = [str(val) for val in range(3)]

        self.assertEquals(call(Command.ECHO, params), None)
        echo.assert_called_once_with(params)


if __name__ == "__main__":
    main()
