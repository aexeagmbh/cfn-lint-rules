from typing import List

import pytest

from cfn_lint_ax.rules import CodeBuildProjectCloudWatchLogs
from tests.utils import BAD_TEMPLATE_FIXTURES_PATH, ExpectedError, assert_all_matches


@pytest.mark.parametrize(
    "filename,expected_errors",
    [
        (
            "codebuild_project.yaml",
            [
                (
                    5,
                    CodeBuildProjectCloudWatchLogs,
                    "Property Resources/Project1/Properties/LogsConfig/CloudWatchLogs/GroupName is missing. CodeBuild projects with cloudwatch logs enabled, should have a GroupName defined.",
                ),
                (
                    31,
                    CodeBuildProjectCloudWatchLogs,
                    "Property Resources/Project2/Properties/LogsConfig/CloudWatchLogs/GroupName is missing. CodeBuild projects with cloudwatch logs enabled, should have a GroupName defined.",
                ),
                (
                    49,
                    CodeBuildProjectCloudWatchLogs,
                    "Property Resources/Project3/Properties/LogsConfig/CloudWatchLogs/GroupName should be a Ref to a LogGroup.",
                ),
                (
                    72,
                    CodeBuildProjectCloudWatchLogs,
                    "Property Resources/Project4/Properties/LogsConfig/CloudWatchLogs/GroupName should be a Ref to a LogGroup.",
                ),
            ],
        ),
    ],
)
def test_bad_code_build_project_log_group(
    filename: str, expected_errors: List[ExpectedError]
) -> None:
    filename = (BAD_TEMPLATE_FIXTURES_PATH / filename).as_posix()

    assert_all_matches(filename, expected_errors)
