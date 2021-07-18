#!/bin/sh -ex
pycodestyle \
    --ignore=W503 --show-source --statistics --count --max-line-length=79 \
    --indent-size=4 .
