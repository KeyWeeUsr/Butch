#!/bin/sh -ex
pycodestyle \
    --ignore=W503 --show-source --statistics --count --max-line-length=79 \
    --indent-size=4 .

pylint \
    caller.py charlist.py commands.py constants.py context.py counter.py \
    filmbuffer.py grammar.py help.py main.py outputs.py parser.py shared.py \
    test.py tokenizer.py \
    --jobs=0 \
    --max-line-length=79 \
    --single-line-if-stmt=n \
    --single-line-class-stmt=n \
    --indent-after-paren=4 \
    --expected-line-ending-format=LF
    --logging-format-style=old
    --init-import=yes \
    --indent-string='    ' \
    --allow-global-unused-variables=n \
    --check-str-concat-over-line-jumps=n \
    --check-quote-consistency=y \
    --import-graph=imports.gv \
    --analyse-fallback-blocks=y \
    --allow-wildcard-with-all=n \
    --good-names="" \
    --include-naming-hint=y \
    --argument-naming-style=snake_case \
    --attr-naming-style=snake_case \
    --class-naming-style=PascalCase \
    --class-attribute-naming-style=snake_case \
    --class-const-naming-style=UPPER_CASE
    --const-naming-style=UPPER_CASE \
    --function-naming-style=snake_case \
    --inlinevar-naming-style=snake_case \
    --method-naming-style=snake_case \
    --module-naming-style=snake_case \
    --variable-naming-style=snake_case
