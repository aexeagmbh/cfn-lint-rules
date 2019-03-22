from pathlib import Path

import cfnlint.decode.cfn_yaml
import pytest
from cfnlint import Runner
from cfnlint.core import get_rules

GOOD_TEMPLATE_FIXTURES_PATH = Path("tests/good").resolve()
BAD_TEMPLATE_FIXTURES_PATH = Path("tests/bad").resolve()


@pytest.mark.parametrize(
    "filename", (p.name for p in GOOD_TEMPLATE_FIXTURES_PATH.glob("*.yaml"))
)
def test_good(filename):
    filename = "tests/good/s3_bucket.yaml"
    regions = ["us-east-1"]

    template = cfnlint.decode.cfn_yaml.load(filename)
    rules = get_rules(
        ["rules"], ignore_rules=[], include_rules=["I"], include_experimental=True
    )

    good_runner = Runner(rules, filename, template, regions, [])
    good_runner.transform()
    errs = good_runner.run()

    assert not errs, errs


@pytest.mark.parametrize(
    "filename,error_count",
    [
        ("s3_bucket_with_bad_public_access_block_configuration.yaml", 4),
        ("s3_bucket_without_bucket_encryption.yaml", 1),
        ("s3_bucket_without_public_access_block_configuration.yaml", 1),
    ],
)
def test_bad(filename, error_count):
    regions = ["us-east-1"]
    filename = BAD_TEMPLATE_FIXTURES_PATH / filename

    template = cfnlint.decode.cfn_yaml.load(filename)
    rules = get_rules(
        ["rules"], ignore_rules=[], include_rules=["I"], include_experimental=True
    )

    good_runner = Runner(
        rules=rules, filename=filename, template=template, regions=regions
    )
    good_runner.transform()
    errs = good_runner.run()

    assert len(errs) == error_count, errs
