#!/usr/bin/env bash

set -ex


pytest
black .
pylama
isort .
yamllint tests/good/*.yaml tests/bad/*.yaml docker-compose.yml .yamllint .travis.yml .cfnlintrc
