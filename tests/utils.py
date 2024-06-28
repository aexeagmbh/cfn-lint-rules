from logging import getLogger
from pathlib import Path
from typing import List, Tuple, Type

import cfnlint.decode.cfn_yaml
from cfnlint.config import ConfigMixIn
from cfnlint.core import get_rules
from cfnlint.rules import CloudFormationLintRule, Match
from cfnlint.runner import TemplateRunner

logger = getLogger(__name__)

ExpectedError = Tuple[int, Type[CloudFormationLintRule], str]

BAD_TEMPLATE_FIXTURES_PATH = Path("tests/bad").resolve()
GOOD_TEMPLATE_FIXTURES_PATH = Path("tests/good").resolve()


def get_cnflint_errors(template_path: str, region: str = "us-east-1") -> List[Match]:
    template = cfnlint.decode.cfn_yaml.load(template_path)
    rules = get_rules(
        ["cfn_lint_ax.rules"],
        ignore_rules=[],
        include_rules=["I"],
        include_experimental=True,
    )
    runner = TemplateRunner(
        filename=template_path,
        template=template,
        config=ConfigMixIn(["--regions", region]),
        rules=rules,
    )
    return list(runner.run())
