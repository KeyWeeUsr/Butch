from commands import Command
from parser import parse, clear_input
from caller import call
from context import get_context


def main():
    while True:
        ctx = get_context()
        inp = input(f"{ctx.cwd} >")
        inp = clear_input(inp)
        if not inp:
            continue

        cmd, params = parse(inp)
        call(cmd, params)


if __name__ == "__main__":
    main()
