#!/bin/sh
PKG="butch"
coverage run \
    --branch \
    --source $PKG \
    --module unittest \
        discover \
        --failfast \
        --catch \
        --start-directory $PKG \
        --top-level-directory $PKG

coverage report --show-missing
