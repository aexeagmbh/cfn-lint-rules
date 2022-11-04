#!/usr/bin/env bash

set -ex


black .
isort .
python -m flake8 .
python -m pytest --pylint -m pylint cfn_lint_ax --pylint-rcfile=$(pwd)/pyproject.toml --pylint-jobs=0
mypy .
yamllint --strict tests/good/*.yaml tests/bad/*.yaml docker-compose.yml .yamllint .cfnlintrc .github/workflows/*.yml
pytest
python3 -m build .
python3 -m twine check dist/*
