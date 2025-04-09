#!/usr/bin/env bash

echo "Running pyup_dirs..."
# pyup_dirs --py39-plus --recursive mcp_servers examples tests docs

echo "Running ruff linter (isort, flake, pyupgrade, etc. replacement)..."
ruff check

echo "Running ruff formatter (black replacement)..."
ruff format

echo "Running codespell to find typos..."
codespell --skip="./node_modules,./playwright-report"
