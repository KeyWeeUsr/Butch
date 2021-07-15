from os.path import abspath, dirname, join
from commands import Command


def print_help(cmd: Command):
    folder = dirname(abspath(__file__))
    with open(join(folder, "help", f"{cmd.value.lower()}.txt")) as file:
        print(file.read())
