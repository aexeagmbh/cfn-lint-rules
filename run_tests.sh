#!/usr/bin/env bash

set -ex


pytest
black .
isort .
pylama
mypy .
yamllint tests/good/*.yaml tests/bad/*.yaml docker-compose.yml .yamllint .cfnlintrc .github/workflows/*.yml
python3 -m build --sdist --wheel .
python3 -m twine check dist/*
