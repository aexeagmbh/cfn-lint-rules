import re
from typing import List

from cfnlint.rules import CloudFormationLintRule


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
