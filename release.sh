#!/bin/sh -ex
git add .
git stash
git clean -dxf
python setup.py bdist_wheel
tree dist
