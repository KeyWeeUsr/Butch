# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch
from os.path import exists


class Caller(TestCase):
    def test_map_resolve_new(self):
        from butch.caller import new_call as call
        from butch.context import Context
        from butch.commandtype import CommandType
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
        from butch.commandtype import CommandType
        from butch.tokenizer import Command, Argument
        from butch.context import Context
        params = [str(val) for val in range(3)]

        with self.assertRaises(UnknownCommand):
            new_call(Command(cmd=CommandType.UNKNOWN, args=[
                Argument(value=value) for value in params
            ]), ctx=Context())

    def test_output_redirection(self):
        from os import remove
        from tempfile import NamedTemporaryFile
        from butch.caller import _handle_redirection_output as handle
        from butch.context import Context
        from butch.outputs import CommandOutput

        output_content = ["hello\n", "butch\n"]
        output = CommandOutput()
        for line in output_content:
            output.stdout.write(line)
        output.stdout.seek(0)

        ctx = Context()
        ctx.output = output

        with NamedTemporaryFile(mode="w+", delete=False) as tmpfile:
            tmp_path = tmpfile.name
            handle(redir_target=tmp_path.replace("/", "\\"), ctx=ctx)
            self.assertTrue(exists(tmp_path))
            tmpfile.seek(0)
            lines = tmpfile.readlines()
            self.assertEqual(lines, output_content)
            remove(tmp_path)
            self.assertFalse(exists(tmp_path))

    def test_input_redirection(self):
        from os import remove
        from tempfile import NamedTemporaryFile
        from butch.caller import _handle_redirection_input as handle
        from butch.context import Context

        input_content = ["hello\n", "butch\n"]

        ctx = Context()

        with NamedTemporaryFile(mode="w+", delete=False) as tmpfile:
            for line in input_content:
                tmpfile.write(line)
            tmpfile.seek(0)

            tmp_path = tmpfile.name
            handle(redir_target=tmp_path.replace("/", "\\"), ctx=ctx)
            self.assertTrue(exists(tmp_path))
            lines = ctx.input.stdin.readlines()
            self.assertEqual(lines, input_content)
            remove(tmp_path)

    def test_trigger_input_redirect(self):
        from butch.caller import new_call, UnknownCommand
        from butch.commandtype import CommandType
        from butch.context import Context
        from butch.tokenizer import Command, File, Redirection, RedirType

        ctx = Context()
        self.assertFalse(ctx.collect_output)
        redir_mock = patch(
            "butch.caller._handle_redirection_input",
            side_effect=UnknownCommand()
        )
        file_path = "<nonexisting>"

        with redir_mock as redir, self.assertRaises(UnknownCommand):
            new_call(cmd=Redirection(
                redir_type=RedirType.INPUT,
                left=Command(cmd=CommandType.UNKNOWN),
                right=File(value=file_path)
            ), ctx=ctx, child=False)
        self.assertFalse(ctx.collect_output)
        self.assertFalse(ctx.piped)

    def test_trigger_output_redirect(self):
        from butch.caller import new_call, UnknownCommand
        from butch.commandtype import CommandType
        from butch.context import Context
        from butch.tokenizer import Command, File, Redirection, RedirType

        ctx = Context()
        self.assertFalse(ctx.collect_output)
        redir_mock = patch(
            "butch.caller._handle_redirection_output",
            side_effect=UnknownCommand()
        )
        file_path = "<nonexisting>"

        with redir_mock as redir, self.assertRaises(UnknownCommand):
            new_call(cmd=Redirection(
                redir_type=RedirType.OUTPUT,
                left=Command(cmd=CommandType.UNKNOWN),
                right=File(value=file_path)
            ), ctx=ctx, child=False)
        self.assertTrue(ctx.collect_output)
        self.assertFalse(ctx.piped)


if __name__ == "__main__":
    main()
