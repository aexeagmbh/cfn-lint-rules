from typing import List

import pytest

from cfn_lint_ax.rules import EcsServiceFargatePlatformVersionNotOutdated
from tests.utils import BAD_TEMPLATE_FIXTURES_PATH, ExpectedError, assert_all_matches


@pytest.mark.parametrize(
    "filename,expected_errors",
    [
        (
            "ecs_fargate_cluster.yaml",
            [
                (
                    10,
                    EcsServiceFargatePlatformVersionNotOutdated,
                    "Resources/ECSService/Properties/PlatformVersion 1.3.0 is outdated. Set it to one of:  LATEST, 1.4.0",
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
