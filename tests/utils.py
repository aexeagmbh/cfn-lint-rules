from logging import getLogger
from pathlib import Path

from cfnlint.config import ConfigMixIn
from cfnlint.core import get_rules
from cfnlint.rules import CloudFormationLintRule, Match
from cfnlint.runner import run_template_by_file_path

logger = getLogger(__name__)

ExpectedError = tuple[int, type[CloudFormationLintRule], str]

BAD_TEMPLATE_FIXTURES_PATH = Path("tests/bad").resolve()
GOOD_TEMPLATE_FIXTURES_PATH = Path("tests/good").resolve()


def get_cnflint_errors(template_path: str, region: str = "us-east-1") -> list[Match]:
    rules = get_rules(
        ["cfn_lint_ax.rules"],
        ignore_rules=[],
        include_rules=["I"],
        include_experimental=True,
    )
    return list(
        run_template_by_file_path(
            filename=template_path,
            config=ConfigMixIn(["--regions", region]),
            rules=rules,
            ignore_bad_template=False,
        )
    )
