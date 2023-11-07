from decimal import Decimal
from typing import List

from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class CodeBuildProjectCloudWatchLogs(CloudFormationLintRule):  # type: ignore[misc]
    """Rule description"""

    id = "W9306"
    shortdesc = "Configure CodeBuild Project CloudWatchLogs"
    description = (
        "If CodeBuild Project CloudWatchLogs are enabled a, define a GroupName."
    )
    # source_url = ""
    tags = ["codebuild", "logging"]

    def match(self, cfn: Template) -> List[RuleMatch]:
        matches = []

        projects = cfn.get_resources(["AWS::CodeBuild::Project"])
        log_groups = cfn.get_resources(["AWS::Logs::LogGroup"])
        for resource_name, resource in projects.items():
            properties = resource.get("Properties", {})
            logs_config = properties.get("LogsConfig", {})
            cloud_watch_logs = logs_config.get("CloudWatchLogs", {})
            path = [
                "Resources",
                resource_name,
                "Properties",
                "LogsConfig",
                "CloudWatchLogs",
                "GroupName",
            ]
            if cloud_watch_logs.get(
                "Status", "ENABLED"
            ) == "ENABLED" and not cloud_watch_logs.get("GroupName"):
                message = f"Property {'/'.join(path)} is missing. CodeBuild projects with cloudwatch logs enabled, should have a GroupName defined."
                matches.append(RuleMatch(path, message))

            group_name = cloud_watch_logs.get("GroupName")
            if group_name and (
                not isinstance(group_name, dict)
                or group_name.get("Ref") not in log_groups.keys()
            ):
                message = f"Property {'/'.join(path)} should be a Ref to a LogGroup."
                matches.append(RuleMatch(path, message))
        return matches


class CodeBuildProjectImage(CloudFormationLintRule):  # type: ignore[misc]
    id = "W9310"
    shortdesc = "Use standard CodeBuild image in latest version"
    description = (
        "If using an AWS CodeBuild image,"
        " it should be the latest version of the standard one."
    )
    # source_url = ""
    tags = ["codebuild"]

    standard_image_min_version = {
        "aws/codebuild/standard": 5,
        "aws/codebuild/amazonlinux2-x86_64-standard": 4,
        "aws/codebuild/amazonlinux2-aarch64-standard": 2,
    }

    def match(self, cfn: Template) -> List[RuleMatch]:
        matches = []

        projects = cfn.get_resources(["AWS::CodeBuild::Project"])
        for resource_name, resource in projects.items():
            if not (properties := resource.get("Properties", {})):
                continue
            if not (environment := properties.get("Environment", {})):
                continue

            path = ["Resources", resource_name, "Properties", "Environment", "Image"]
            image = environment.get("Image") or ""
            if not image.startswith("aws/codebuild/"):
                continue
            if not (
                image.startswith("aws/codebuild/standard:")
                or image.startswith("aws/codebuild/amazonlinux2-x86_64-standard:")
                or image.startswith("aws/codebuild/amazonlinux2-aarch64-standard:")
            ):
                message = (
                    f"Property {'/'.join(path)} uses an AWS image other than standard."
                )
                matches.append(RuleMatch(path, message))
                continue
            if ":" in image:
                image_name, image_version = image.split(":", maxsplit=1)
                if Decimal(image_version) < self.standard_image_min_version[image_name]:
                    message = (
                        f"Property {'/'.join(path)} uses an outdated version"
                        " of the standard image."
                    )
                    matches.append(RuleMatch(path, message))
        return matches
