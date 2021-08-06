# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class SetlocalCommand(TestCase):
    def test_setlocal_help(self):
        import sys
        from butch.context import Context
        from butch.commands import setlocal
        from butch.commandtype import CommandType
        from butch.tokens import Argument
        from butch.constants import PARAM_HELP

        ctx = Context()
        with patch("butch.commands.print_help") as prnt:
            setlocal(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(cmd=CommandType.SETLOCAL, file=sys.stdout)

        ctx.collect_output = True
        with patch("butch.commands.print_help") as prnt:
            setlocal(params=[Argument(value=PARAM_HELP)], ctx=ctx)
        prnt.assert_called_once_with(
            cmd=CommandType.SETLOCAL, file=ctx.output.stdout
        )

    def test_setlocal_enable_expansion(self):
        from butch.context import Context
        from butch.commands import setlocal
        from butch.tokens import Argument

        ctx = Context()
        ctx.delayed_expansion_enabled = False
        self.assertFalse(ctx.delayed_expansion_enabled)
        setlocal(params=[Argument(value="enabledelayedexpansion")], ctx=ctx)
        self.assertTrue(ctx.delayed_expansion_enabled)

    def test_setlocal_disable_expansion(self):
        from butch.context import Context
        from butch.commands import setlocal
        from butch.tokens import Argument

        ctx = Context()
        ctx.delayed_expansion_enabled = True
        self.assertTrue(ctx.delayed_expansion_enabled)
        setlocal(params=[Argument(value="disabledelayedexpansion")], ctx=ctx)
        self.assertFalse(ctx.delayed_expansion_enabled)

    def test_setlocal_enable_extensions(self):
        from butch.context import Context
        from butch.commands import setlocal
        from butch.tokens import Argument

        ctx = Context()
        ctx.extensions_enabled = False
        self.assertFalse(ctx.extensions_enabled)
        setlocal(params=[Argument(value="enableextensions")], ctx=ctx)
        self.assertTrue(ctx.extensions_enabled)

    def test_setlocal_disable_extensions(self):
        from butch.context import Context
        from butch.commands import setlocal
        from butch.tokens import Argument

        ctx = Context()
        ctx.extensions_enabled = True
        self.assertTrue(ctx.extensions_enabled)
        setlocal(params=[Argument(value="disableextensions")], ctx=ctx)
        self.assertFalse(ctx.extensions_enabled)

    def test_setlocal_unknown(self):
        from butch.context import Context
        from butch.commands import setlocal
        from butch.tokens import Argument

        ctx = Context()
        self.assertFalse(ctx.delayed_expansion_enabled)
        self.assertTrue(ctx.extensions_enabled)
        setlocal(params=[Argument(value="unknown")], ctx=ctx)
        self.assertFalse(ctx.delayed_expansion_enabled)
        self.assertTrue(ctx.extensions_enabled)

    def test_setlocal_nyi(self):
        from butch.context import Context
        from butch.commands import setlocal
        from butch.tokens import Argument

        ctx = Context()
        with self.assertRaises(NotImplementedError):
            setlocal(params=[], ctx=ctx)
