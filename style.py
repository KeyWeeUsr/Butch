import sys
from os import walk
from os.path import join
from glob import glob
from subprocess import Popen, PIPE


def main():
    proc = Popen([
        "pycodestyle", "--ignore=W503", "--show-source", "--statistics",
        "--count", "--max-line-length=79", "--indent-size=4", "."
    ])
    proc.communicate()
    if proc.returncode:
        sys.exit(proc.returncode)

    proc = Popen([
        "pylint", "--jobs=0",
        # "--exit-zero",
        "--max-line-length=79",
        "--single-line-if-stmt=n",
        "--single-line-class-stmt=n",
        "--indent-after-paren=4",
        "--expected-line-ending-format=LF",
        "--logging-format-style=old",
        "--init-import=yes",
        "--indent-string='    '",
        "--check-str-concat-over-line-jumps=n",
        "--check-quote-consistency=y",
        "--import-graph=imports.gv",
        "--analyse-fallback-blocks=y",
        "--allow-wildcard-with-all=n",
        "--good-names=""",
        "--include-naming-hint=y",
        "--argument-naming-style=snake_case",
        "--attr-naming-style=snake_case",
        "--class-naming-style=PascalCase",
        "--class-attribute-naming-style=snake_case",
        "--class-const-naming-style=UPPER_CASE",
        "--const-naming-style=UPPER_CASE",
        "--function-naming-style=snake_case",
        "--inlinevar-naming-style=snake_case",
        "--method-naming-style=snake_case",
        "--module-naming-style=snake_case",
        "--variable-naming-style=snake_case",
        *glob("butch/*.py")
    ])
    proc.communicate()
    if proc.returncode:
        sys.exit(proc.returncode)

    # wtf codes:
    # WPS412, I005
    # I004 it's called readability...
    # WPS336 straight-forward nonsense unless customizable per package/module
    # WPS305 "f strings implicitly rely on the context around them"
    # - so do functions as well as string.format() can be used as template
    # WPS323 there's a lot of logging and % is actually useful in there
    proc = Popen([
        "flake8",
        "--inline-quotes=double",
        "--inline-quotes=double",
        "--multiline-quotes", '"""',
        "--docstring-quotes", '"',
        "--avoid-escape",
        "--ignore", ",".join([
            "C812", "WPS421", "WPS326", "I005", "I004", "WPS336", "WPS305",
            "WPS306", "WPS327", "WPS323"
        ]),
        "--per-file-ignores", "butch/commandtype.py:WPS115",
        "--max-module-members=10",
        "--allowed-domain-names", "param,params", "."
    ], stdout=PIPE)
    stdout, _ = proc.communicate()

    lines = [
        line for line in stdout.decode("utf-8").splitlines()
        if "WPS412" not in line
    ]
    count = 0
    for line in lines:
        print(line, file=sys.stderr)
        count += 1

    total = 0
    for root, _, files in walk('.'):
        for file in files:
            if not file.endswith('.py'):
                continue
            with open(join(root, file)) as fdes:
                total += len(fdes.readlines())

    perc = count / total * 100
    print(f"{count} / {total} ({perc:.02f}%)")
    if proc.returncode:
        sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
