#!/usr/bin/env bash

set -ex


pytest
black .
pylama
isort --recursive
yamllint tests/good/*.yaml tests/bad/*.yaml docker-compose.yml .yamllint .travis.yml .cfnlintrc
pipenv check
pipenv check --unused rules || true
