from typing import List

import pytest

from rules.cloudfront_distribution_comment import CloudfrontDistributionComment
from rules.cloudfront_distribution_logging import CloudfrontDistributionLogging
from tests.utils import BAD_TEMPLATE_FIXTURES_PATH, ExpectedError, assert_all_matches


@pytest.mark.parametrize(
    "filename,expected_errors",
    [
        (
            "cloudfront_distribution_without_logging_configuration.yaml",
            [
                (
                    6,
                    CloudfrontDistributionLogging,
                    "Property Resources/Distribution/Properties/DistributionConfig/Logging is missing",
                ),
            ],
        ),
        (
            "cloudfront_distribution_without_comment.yaml",
            [
                (
                    6,
                    CloudfrontDistributionComment,
                    "Property Resources/Distribution/Properties/DistributionConfig/Comment is missing",
                ),
            ],
        ),
    ],
)
def test_bad_cloudfront_distribution_config(
    filename: str, expected_errors: List[ExpectedError]
) -> None:
    filename = (BAD_TEMPLATE_FIXTURES_PATH / filename).as_posix()

    assert_all_matches(filename, expected_errors)
