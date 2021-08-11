#!/bin/sh -e
PKG="butch"
PATTERN=${PATTERN:-'test*.py'}
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
