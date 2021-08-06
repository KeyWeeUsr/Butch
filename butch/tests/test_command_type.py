# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class TypeCommand(TestCase):
    def test_type_piped_single(self):
        import sys
        from os.path import abspath
        from butch.context import Context
        from butch.commands import type_cmd
        from butch.tokens import Argument

        dummy = "dummy"

        ctx = Context()
        ctx.collect_output = True
        type_cmd(params=[Argument(value=abspath(__file__))], ctx=ctx)

        pipe = ctx.output.stdout
        self.assertEqual(pipe.read(), "")  # no seek
        pipe.seek(0)
        with open(__file__) as this_file:
            self.assertEqual(pipe.read(), this_file.read() + "\n")

    def test_type_piped_multi(self):
        import sys
        from os.path import abspath
        from butch.context import Context
        from butch.commands import type_cmd
        from butch.tokens import Argument

        dummy = "dummy"

        ctx = Context()
        ctx.collect_output = True
        path = abspath(__file__)
        type_cmd(params=[Argument(value=path)] * 2, ctx=ctx)

        pipe = ctx.output.stdout
        self.assertEqual(pipe.read(), "")  # no seek
        pipe.seek(0)
        with open(__file__) as this_file:
            body = this_file.read()
            self.assertEqual(
                pipe.read(),
                f"{path}\n\n\n\n\n{body}\n\n\n{path}\n\n\n\n\n{body}\n"
            )

    def test_type_no_args(self):
        import sys
        from butch.context import Context
        from butch.constants import SYNTAX_INCORRECT
        from butch.commands import type_cmd

        ctx = Context()
        ctx.collect_output = True
        self.assertEqual(ctx.error_level, 0)
        type_cmd(params=[], ctx=ctx)
        self.assertEqual(ctx.error_level, 1)

        pipe = ctx.output.stdout
        self.assertEqual(pipe.read(), "")  # no seek
        pipe.seek(0)
        self.assertEqual(pipe.read(), SYNTAX_INCORRECT + "\n")

    def test_type_help(self):
        import sys
        from butch.context import Context
        from butch.constants import PARAM_HELP
        from butch.commands import type_cmd
        from butch.commandtype import CommandType
        from butch.tokens import Argument

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            type_cmd(params=[Argument(value=PARAM_HELP)], ctx=ctx)

        prnt.assert_called_once_with(cmd=CommandType.TYPE, file=sys.stdout)

    def test_type_folder(self):
        import sys
        from os.path import abspath, dirname
        from butch.context import Context
        from butch.commands import type_cmd
        from butch.constants import ACCESS_DENIED
        from butch.tokens import Argument

        dummy = "dummy"

        ctx = Context()
        ctx.collect_output = True
        type_cmd(params=[Argument(value=dirname(abspath(__file__)))], ctx=ctx)

        pipe = ctx.output.stdout
        self.assertEqual(pipe.read(), "")  # no seek
        pipe.seek(0)
        with open(__file__) as this_file:
            self.assertEqual(pipe.read(), ACCESS_DENIED + "\n")

    def test_type_nonexisting_single(self):
        import sys
        from os.path import abspath, dirname
        from butch.context import Context
        from butch.commands import type_cmd
        from butch.constants import FILE_NOT_FOUND
        from butch.tokens import Argument

        dummy = "dummy"

        ctx = Context()
        ctx.collect_output = True
        type_cmd(params=[Argument(value=dummy)], ctx=ctx)

        pipe = ctx.output.stdout
        self.assertEqual(pipe.read(), "")  # no seek
        pipe.seek(0)
        with open(__file__) as this_file:
            self.assertEqual(pipe.read(), FILE_NOT_FOUND + "\n")

    def test_type_folder_multi(self):
        import sys
        from os.path import abspath, dirname
        from butch.context import Context
        from butch.commands import type_cmd
        from butch.constants import ACCESS_DENIED, ERROR_PROCESSING
        from butch.tokens import Argument

        dummy = "dummy"

        ctx = Context()
        ctx.collect_output = True
        path = dirname(abspath(__file__))
        type_cmd(params=[Argument(value=path)] * 2, ctx=ctx)

        pipe = ctx.output.stdout
        self.assertEqual(pipe.read(), "")  # no seek
        pipe.seek(0)
        error = ERROR_PROCESSING.format(path)
        self.assertEqual(
            pipe.read(), f"{path}\n{ACCESS_DENIED}\n{error}\n" * 2
        )

    def test_type_nonexisting_multi(self):
        import sys
        from os.path import abspath, dirname
        from butch.context import Context
        from butch.commands import type_cmd
        from butch.constants import FILE_NOT_FOUND, ERROR_PROCESSING
        from butch.tokens import Argument

        dummy = "dummy"

        ctx = Context()
        ctx.collect_output = True
        type_cmd(params=[Argument(value=dummy)] * 2, ctx=ctx)

        pipe = ctx.output.stdout
        self.assertEqual(pipe.read(), "")  # no seek
        pipe.seek(0)
        error = ERROR_PROCESSING.format(dummy)
        self.assertEqual(
            pipe.read(), f"{dummy}\n{FILE_NOT_FOUND}\n{error}\n" * 2
        )
