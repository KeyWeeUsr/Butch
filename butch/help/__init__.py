"""Module for reading the help files from "help" folder."""

import sys
from os.path import abspath, dirname, join

from butch.commands import Command


def print_help(cmd: Command, file=sys.stdout):  # noqa: WPS110
    """
    Open a help file for passed Command and print it.

    Args:
        cmd: Command instance
        file: file or standard output/error (default: sys.stdout)
    """
    folder = dirname(abspath(__file__))
    name = cmd.value.lower()
    with open(join(folder, f"{name}.txt")) as fdes:
        print(fdes.read(), file=file)
