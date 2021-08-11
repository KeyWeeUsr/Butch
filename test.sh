#!/bin/sh -e
PKG="butch"
PATTERN=${PATTERN:-'test*.py'}
HTML=${HTML:-""}
HTML_OPEN=${HTML_OPEN:-""}
coverage run \
    --branch \
    --source $PKG \
    --module unittest \
        discover \
        --pattern $PATTERN \
        --failfast \
        --catch \
        --start-directory $PKG \
        --top-level-directory $PKG $*

coverage report --show-missing --omit 'butch/tests/*'

if [ "$HTML" = "1" ]
then
    coverage html
    if [ "$HTML_OPEN" = "1" ]
    then
        xdg-open htmlcov/index.html
    fi
fi
