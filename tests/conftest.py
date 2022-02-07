from typing import List

import pytest
from _pytest.fixtures import SubRequest
from cfnlint.core import get_rules
from cfnlint.rules import CloudFormationLintRule

from tests.utils import BAD_TEMPLATE_FIXTURES_PATH, GOOD_TEMPLATE_FIXTURES_PATH

_ax_rules: List[CloudFormationLintRule] = [
    rule
    for rule in get_rules(["cfn_lint_ax.rules"], [], [])
    if rule.__module__.startswith("cfn_lint_ax.rules.")
]


@pytest.fixture(name="ax_rules")
def fixture_ax_rules() -> List[CloudFormationLintRule]:
    return _ax_rules.copy()


@pytest.fixture(name="ax_rule", params=_ax_rules)
def fixture_ax_rule(request: SubRequest) -> CloudFormationLintRule:
    return request.param


_bad_templates = [p.name for p in BAD_TEMPLATE_FIXTURES_PATH.glob("*.yaml")]
_good_templates = [p.name for p in GOOD_TEMPLATE_FIXTURES_PATH.glob("*.yaml")]


@pytest.fixture(
    name="bad_templates",
)
def fixture_bad_templates() -> List[str]:
    return _bad_templates.copy()


@pytest.fixture(name="bad_template", params=_bad_templates)
def fixture_bad_template(request: SubRequest) -> str:
    return request.param


@pytest.fixture(name="good_template", params=_good_templates)
def fixture_good_template(request: SubRequest) -> str:
    return request.param
