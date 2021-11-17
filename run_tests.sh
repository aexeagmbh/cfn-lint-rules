#!/usr/bin/env bash

set -ex


black .
isort .
pylama
mypy .
yamllint --strict tests/good/*.yaml tests/bad/*.yaml docker-compose.yml .yamllint .cfnlintrc .github/workflows/*.yml
pytest
python3 -m build --sdist --wheel .
python3 -m twine check dist/*
