#!/usr/bin/env bash

set -ex


black .
isort .
python -m flake8 .
python -m pylint --recursive=y --reports=y --verbose ./
mypy .
yamllint --strict tests/good/*.yaml tests/bad/*.yaml docker-compose.yml .yamllint .cfnlintrc .github/workflows/*.yml
pytest
python3 -m build .
python3 -m twine check dist/*
