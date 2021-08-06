# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase
from unittest.mock import patch, MagicMock


class Utils(TestCase):
    def test_print_all_vars(self):
        import sys
        from butch.context import Context
        from butch.commands import _print_all_variables
        from unittest.mock import call

        ctx = Context()
        with patch("butch.commands.print") as prnt:
            _print_all_variables(ctx=ctx, file=sys.stdout)
            self.assertEqual(prnt.call_count, len(ctx.variables))

    def test_print_single_var_undefined(self):
        import sys
        from butch.context import Context
        from butch.commands import _print_single_variable
        from butch.constants import ENV_VAR_UNDEFINED
        from unittest.mock import call

        ctx = Context()
        ctx.get_variable = MagicMock(return_value=False)

        dummy = "dummy"
        with patch("butch.commands.print") as prnt:
            _print_single_variable(key=dummy, ctx=ctx, file=sys.stdout)
        prnt.assert_called_once_with(ENV_VAR_UNDEFINED, file=sys.stdout)
        ctx.get_variable.assert_called_once_with(key=dummy)

    def test_print_single_var_defined(self):
        import sys
        from butch.context import Context
        from butch.commands import _print_single_variable
        from unittest.mock import call

        ctx = Context()
        found_value = "found"
        ctx.get_variable = MagicMock(return_value=found_value)

        dummy = "dummy"
        with patch("butch.commands.print") as prnt:
            _print_single_variable(key=dummy, ctx=ctx, file=sys.stdout)
        prnt.assert_called_once_with(f"{dummy}={found_value}", file=sys.stdout)
        ctx.get_variable.assert_called_once_with(key=dummy)
