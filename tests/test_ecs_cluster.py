from typing import List

import pytest

from cfn_lint_ax.rules import (
    EcsServiceDeploymentConfiguration,
    EcsServiceFargatePlatformVersionNotOutdated,
)
from tests.utils import BAD_TEMPLATE_FIXTURES_PATH, ExpectedError, assert_all_matches


@pytest.mark.parametrize(
    "filename,expected_errors",
    [
        (
            "ecs_fargate_cluster.yaml",
            [
                (
                    5,
                    EcsServiceDeploymentConfiguration,
                    "Resources/ECSService/Properties/DeploymentConfiguration Property DeploymentConfiguration is missing.",
                ),
                (
                    5,
                    EcsServiceDeploymentConfiguration,
                    "Resources/ECSService/Properties/DeploymentConfiguration/DeploymentCircuitBreaker Property DeploymentConfiguration/DeploymentCircuitBreaker is missing.",
                ),
                (
                    5,
                    EcsServiceDeploymentConfiguration,
                    "Resources/ECSService/Properties/DeploymentConfiguration/DeploymentCircuitBreaker/Enable Property DeploymentConfiguration/DeploymentCircuitBreaker/Enable should be true.",
                ),
                (
                    5,
                    EcsServiceDeploymentConfiguration,
                    "Resources/ECSService/Properties/DeploymentConfiguration/DeploymentCircuitBreaker/Rollback Property DeploymentConfiguration/DeploymentCircuitBreaker/Rollback should be false.",
                ),
                (
                    10,
                    EcsServiceFargatePlatformVersionNotOutdated,
                    "Resources/ECSService/Properties/PlatformVersion 1.3.0 is outdated. Set it to one of:  LATEST, 1.4.0",
                ),
                (
                    22,
                    EcsServiceDeploymentConfiguration,
                    "Resources/ECSServiceDeploymentCircuitBreakerWithBadValues/Properties/DeploymentConfiguration/DeploymentCircuitBreaker/Enable Property DeploymentConfiguration/DeploymentCircuitBreaker/Enable should be true.",
                ),
                (
                    23,
                    EcsServiceDeploymentConfiguration,
                    "Resources/ECSServiceDeploymentCircuitBreakerWithBadValues/Properties/DeploymentConfiguration/DeploymentCircuitBreaker/Rollback Property DeploymentConfiguration/DeploymentCircuitBreaker/Rollback should be false.",
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
