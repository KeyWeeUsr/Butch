import sys
from commands import Command
from parser import parse, clear_input
from caller import call
from context import get_context


def loop():
    while True:
        ctx = get_context()
        inp = input(f"{ctx.cwd} >")
        inp = clear_input(inp)
        if not inp:
            continue

        cmd, params = parse(inp)
        call(cmd, params)


def ctrlc_handler(*_):
    return False


def main():
    while True:
        try:
            loop()
        except KeyboardInterrupt:
            if not ctrlc_handler():
                print()
                continue
        except EOFError:
            sys.exit(0)


if __name__ == "__main__":
    main()
