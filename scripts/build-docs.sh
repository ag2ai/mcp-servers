#!/usr/bin/env bash

export TERMINAL_WIDTH=80

set -e
set -x

# build docs
rm -rf docs/docs/en/api docs/docs/en/cli
cd docs; python docs.py build
