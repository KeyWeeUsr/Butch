"""
Module for reading the help files from "help" folder and dumping the contents
to STDOUT (or other provided buffer, if any).
"""

import sys
from os.path import abspath, dirname, join
from butch.commands import Command


def print_help(cmd: Command, file=sys.stdout):
    "Open a help file for passed Command and print it."
    folder = dirname(abspath(__file__))
    with open(join(folder, "help", f"{cmd.value.lower()}.txt")) as fdes:
        print(fdes.read(), file=file)
