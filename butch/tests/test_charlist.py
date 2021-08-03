# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals

from unittest import main, TestCase


def common(inst, clist, first, second):
    inst.assertEqual(clist.data, first)
    inst.assertEqual(clist._data, first)
    inst.assertTrue(clist)
    inst.assertEqual(str(clist), f"CharList({first!r})")
    inst.assertEqual(repr(clist), f"CharList({first!r})")

    clist += second
    inst.assertEqual(clist.data, first + second)
    inst.assertEqual(clist._data, first + second)
    inst.assertTrue(clist)
    inst.assertEqual(str(clist), f"CharList({first + second!r})")
    inst.assertEqual(repr(clist), f"CharList({first + second!r})")

    clist.clear()
    inst.assertEqual(clist.data, "")
    inst.assertEqual(clist._data, "")
    inst.assertFalse(clist)
    inst.assertEqual(str(clist), f"CharList({''!r})")
    inst.assertEqual(repr(clist), f"CharList({''!r})")

    clist.data = second
    inst.assertEqual(clist.data, second)
    inst.assertEqual(clist._data, second)
    inst.assertTrue(clist)
    inst.assertEqual(str(clist), f"CharList({second!r})")
    inst.assertEqual(repr(clist), f"CharList({second!r})")


class CharLists(TestCase):
    def test_append_arg(self):
        from butch.charlist import CharList

        dummy = "hello"
        appended = "xyz"
        clist = CharList(dummy)
        common(self, clist, dummy, appended)

    def test_append_kwarg(self):
        from butch.charlist import CharList

        dummy = "hello"
        appended = "xyz"
        clist = CharList(data=dummy)
        common(self, clist, dummy, appended)
