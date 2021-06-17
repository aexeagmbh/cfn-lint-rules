import re
from typing import List

import cfnlint.decode.cfn_yaml
import pytest
from _pytest.fixtures import SubRequest
from cfnlint.core import get_rules
from cfnlint.rules import CloudFormationLintRule
from cfnlint.runner import Runner

from tests.utils import BAD_TEMPLATE_FIXTURES_PATH, GOOD_TEMPLATE_FIXTURES_PATH


@pytest.mark.parametrize(
    "filename", (p.as_posix() for p in GOOD_TEMPLATE_FIXTURES_PATH.glob("*.yaml"))
)
def test_good(filename: str) -> None:
    regions = ["us-east-1"]

    template = cfnlint.decode.cfn_yaml.load(filename)
    rules = get_rules(
        ["cfn_lint_ax.rules"],
        ignore_rules=[],
        include_rules=["I"],
        include_experimental=True,
    )

    good_runner = Runner(rules, filename, template, regions, [])
    good_runner.transform()
    errs = good_runner.run()

    assert not errs, errs


@pytest.mark.parametrize(
    "filename,error_count",
    [
        ("ecs_fargate_cluster.yaml", 1),
        ("metadata_ax_changeset_auto_approve.yaml", 9),
        ("s3_bucket_with_bad_public_access_block_configuration.yaml", 5),
        ("s3_bucket_without_bucket_encryption.yaml", 1),
        ("s3_bucket_without_public_access_block_configuration.yaml", 1),
        ("unresolved_object.yaml", 2),
    ],
)
def test_bad(filename: str, error_count: int) -> None:
    regions = ["us-east-1"]
    filename = (BAD_TEMPLATE_FIXTURES_PATH / filename).as_posix()

    template = cfnlint.decode.cfn_yaml.load(filename)
    rules = get_rules(
        ["cfn_lint_ax.rules"],
        ignore_rules=[],
        include_rules=["I"],
        include_experimental=True,
    )

    good_runner = Runner(
        rules=rules, filename=filename, template=template, regions=regions
    )
    good_runner.transform()
    errs = good_runner.run()

    assert len(errs) == error_count, errs


def _ax_rules() -> List[CloudFormationLintRule]:
    rules = get_rules(["cfn_lint_ax.rules"], [], [])
    ax_rules = [
        rule for rule in rules if rule.__module__.startswith("cfn_lint_ax.rules.")
    ]
    return ax_rules


@pytest.fixture(scope="session")
def ax_rules() -> List[CloudFormationLintRule]:
    return _ax_rules()


@pytest.fixture(scope="session", params=_ax_rules())
def ax_rule(request: SubRequest) -> CloudFormationLintRule:
    return request.param


def test_rule_ids_are_unique(ax_rules: List[CloudFormationLintRule]) -> None:
    rule_ids = set()
    for rule in ax_rules:
        assert rule.id not in rule_ids, f"Rule Id {rule.id} is used multiple times"
        rule_ids.add(rule.id)


rule_id_re = re.compile(r"^[IWE]9\d\d\d$")


def test_rule_id(ax_rule: CloudFormationLintRule) -> None:
    assert rule_id_re.match(
        ax_rule.id
    ), f"{ax_rule.__class__} id {ax_rule.id} does not match {rule_id_re.pattern}"
