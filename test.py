import sys
from os import environ
from subprocess import Popen
from webbrowser import open as wopen
PKG = "butch"
PATTERN = environ.get("PATTERN", "test*.py")
HTML = environ.get("HTML", "")
HTML_OPEN = environ.get("HTML_OPEN", "")

def main():
    proc = Popen([
        "coverage", "run",
        "--branch",
        "--source", PKG,
        "--module", "unittest", "discover",
        "--pattern", PATTERN,
        "--failfast",
        "--catch",
        "--start-directory", PKG,
        "--top-level-directory", PKG, *sys.argv[1:]
    ])
    proc.communicate()
    if proc.returncode:
        sys.exit(proc.returncode)

    proc = Popen([
        "coverage", "report", "--show-missing", "--omit", "butch/tests/*"
    ])
    proc.communicate()
    if proc.returncode:
        sys.exit(proc.returncode)

    if HTML == "1":
        proc = Popen(["coverage", "html"])
        proc.communicate()
        if proc.returncode:
            sys.exit(proc.returncode)

    if HTML_OPEN == "1":
        wopen("./htmlcov/index.html")


if __name__ == "__main__":
    main()
