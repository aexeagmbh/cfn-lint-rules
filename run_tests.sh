#!/usr/bin/env bash

set -ex


uv run black .
uv run isort .
uv run flake8 .
uv run pylint --recursive=y --reports=y --verbose ./
uv run mypy .
uv run yamllint --strict tests/good/*.yaml tests/bad/*.yaml .yamllint .cfnlintrc .github/workflows/*.yml
uv run pytest
uv build .
uv run --only-group publish twine check dist/*
