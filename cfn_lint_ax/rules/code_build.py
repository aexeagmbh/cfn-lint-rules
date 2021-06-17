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
                or not group_name.get("Ref") in log_groups.keys()
            ):
                message = f"Property {'/'.join(path)} should be a Ref to a LogGroup."
                matches.append(RuleMatch(path, message))
        return matches
