from commands import Command
from parser import parse, clear_input
from caller import call


def main():
    while True:
        inp = input(">")
        inp = clear_input(inp)
        if not inp:
            continue

        cmd, params = parse(inp)
        call(cmd, params)


if __name__ == "__main__":
    main()
