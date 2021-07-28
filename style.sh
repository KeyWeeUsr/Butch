#!/bin/sh -e
pycodestyle \
    --ignore=W503 --show-source --statistics --count --max-line-length=79 \
    --indent-size=4 .

pylint \
    butch/*.py \
    --exit-zero \
    --jobs=0 \
    --max-line-length=79 \
    --single-line-if-stmt=n \
    --single-line-class-stmt=n \
    --indent-after-paren=4 \
    --expected-line-ending-format=LF \
    --logging-format-style=old \
    --init-import=yes \
    --indent-string='    ' \
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
    --class-const-naming-style=UPPER_CASE \
    --const-naming-style=UPPER_CASE \
    --function-naming-style=snake_case \
    --inlinevar-naming-style=snake_case \
    --method-naming-style=snake_case \
    --module-naming-style=snake_case \
    --variable-naming-style=snake_case

# WPS412 wtf???
# I005 double-wtf?
# I004 it's called readability...
# WPS336 straight-forward nonsense unless customizable per package/module
# WPS305 "f strings implicitly rely on the context around them"
# - crap... so do functions as well as string.format() can be used as template
# WPS323 there's a lot of logging and % is actually useful in there
COUNT=$(flake8 \
    --inline-quotes=double \
    --inline-quotes=double \
    --multiline-quotes='"""' \
    --docstring-quotes='"' \
    --avoid-escape \
    --ignore C812,WPS421,WPS326,I005,I004,WPS336,WPS305,WPS306,WPS327,WPS323 \
    --per-file-ignores \
        'butch/commandtype.py:WPS115' \
    --max-module-members=10 \
    --allowed-domain-names param,params \
    . |grep -v WPS412 | tee /dev/stderr | wc -l)
TOTAL=$(find . -name '*.py' -type f -exec cat {} + | wc -l)
PERC=$(python -c "print($COUNT / $TOTAL * 100)")
echo "$COUNT / $(find . -name '*.py' -type f -exec cat {} + | wc -l) ($PERC)"
