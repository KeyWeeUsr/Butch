from .commands import Command
from .parser import parse


def main():
    while True:
        inp = input(">")
        cmd, params = parse(inp)


if __name__ == "__main__":
    main()
