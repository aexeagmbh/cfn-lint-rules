from logging import getLogger
from pathlib import Path
from typing import List, Tuple, Type

import cfnlint.decode.cfn_yaml
from cfnlint.core import get_rules
from cfnlint.rules import CloudFormationLintRule, Match
from cfnlint.runner import Runner

logger = getLogger(__name__)

ExpectedError = Tuple[int, Type[CloudFormationLintRule], str]

BAD_TEMPLATE_FIXTURES_PATH = Path("tests/bad").resolve()
GOOD_TEMPLATE_FIXTURES_PATH = Path("tests/good").resolve()


def get_cnflint_errors(template_path: str, region: str = "us-east-1") -> List[Match]:
    regions = [region]
    template = cfnlint.decode.cfn_yaml.load(template_path)
    rules = get_rules(
        ["cfn_lint_ax.rules"],
        ignore_rules=[],
        include_rules=["I"],
        include_experimental=True,
    )
    runner = Runner(
        rules=rules, filename=template_path, template=template, regions=regions
    )
    runner.transform()
    errors = runner.run()
    return errors
