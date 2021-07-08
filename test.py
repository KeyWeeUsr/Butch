from unittest import main, TestCase


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


if __name__ == "__main__":
    main()
