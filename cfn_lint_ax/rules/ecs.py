from typing import List

from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class EcsServiceFargatePlatformVersionNotOutdated(CloudFormationLintRule):  # type: ignore[misc]
    """Rule description"""

    id = "I9301"
    shortdesc = "Fargate platform version should not be outdated."
    description = "Fargate platform version should not be outdated."
    source_url = "https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html"
    tags = ["ecs", "fargate"]

    def match(self, cfn: Template) -> List[RuleMatch]:
        matches = []

        valid_platform_versions = ["LATEST", "1.4.0"]

        resources = cfn.get_resources(["AWS::ECS::Service"])
        for resource_name, resource in resources.items():
            properties = resource.get("Properties", {})
            if not properties.get("LaunchType") == "FARGATE":
                continue
            platform_version = properties.get("PlatformVersion")
            if platform_version is None:
                continue

            if not platform_version in valid_platform_versions:
                path = ["Resources", resource_name, "Properties", "PlatformVersion"]
                message = f"{'/'.join(path)} {platform_version} is outdated. Set it to one of:  {', '.join(valid_platform_versions)}"
                matches.append(RuleMatch(path, message))

        return matches
