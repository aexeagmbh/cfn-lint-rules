from pathlib import Path

import cfnlint.decode.cfn_yaml
from cfnlint import Runner
from cfnlint.core import get_rules

BAD_TEMPLATE_FIXTURES_PATH = Path("tests/bad").resolve()
GOOD_TEMPLATE_FIXTURES_PATH = Path("tests/good").resolve()


def assert_all_matches(filename, expected_errors, region="us-east-1"):
    regions = [region]
    template = cfnlint.decode.cfn_yaml.load(filename)
    rules = get_rules(
        ["rules"], ignore_rules=[], include_rules=["I"], include_experimental=True
    )
    runner = Runner(rules=rules, filename=filename, template=template, regions=regions)
    runner.transform()
    errs = runner.run()

    for expected_error in expected_errors:
        line_number = expected_error[0]
        lint_rule_class = expected_error[1]
        message = expected_error[2]

        lint_rule_class_name = (
            f"{lint_rule_class.__module__}.{lint_rule_class.__name__}"
        )
        if lint_rule_class_name.startswith("rules."):
            lint_rule_class_name = lint_rule_class_name[len("rules.") :]

        for errs_idx, match in enumerate(errs):
            match_rule_class = match.rule.__class__
            match_rule_class_name = (
                f"{match_rule_class.__module__}.{match_rule_class.__name__}"
            )
            if (
                match.linenumber == line_number
                and match_rule_class_name == lint_rule_class_name
                and match.message == message
            ):
                del errs[errs_idx]
                break
        else:
            assert False, f"{line_number} - {lint_rule_class} - {message} not in errs"
    assert len(errs) == 0, errs
