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
            platform_version = properties.get("PlatformVersion")
            if platform_version is None:
                continue

            if platform_version not in valid_platform_versions:
                path = ["Resources", resource_name, "Properties", "PlatformVersion"]
                message = f"{'/'.join(path)} {platform_version} is outdated. Set it to one of:  {', '.join(valid_platform_versions)}"
                matches.append(RuleMatch(path, message))

        return matches


class EcsServiceDeploymentConfiguration(CloudFormationLintRule):  # type: ignore[misc]
    """Rule description"""

    id = "W9309"
    shortdesc = "ECS Services should have a deployment configuration with DeploymentCircuitBreaker."
    description = "ECS Services should have a deployment configuration with DeploymentCircuitBreaker."
    source_url = "https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-ecs.html#deployment-circuit-breaker"
    tags = ["ecs", "service", "circuit-breaker"]

    def match(self, cfn: Template) -> List[RuleMatch]:
        matches = []

        resources = cfn.get_resources(["AWS::ECS::Service"])
        for resource_name, resource in resources.items():
            properties = resource.get("Properties", {})

            deployment_configuration = properties.get("DeploymentConfiguration", {})
            if not deployment_configuration:
                path = [
                    "Resources",
                    resource_name,
                    "Properties",
                    "DeploymentConfiguration",
                ]
                message = (
                    f"{'/'.join(path)} Property DeploymentConfiguration is missing."
                )
                matches.append(RuleMatch(path, message))

            deployment_circuit_breaker = deployment_configuration.get(
                "DeploymentCircuitBreaker", {}
            )

            if not deployment_circuit_breaker:
                path = [
                    "Resources",
                    resource_name,
                    "Properties",
                    "DeploymentConfiguration",
                    "DeploymentCircuitBreaker",
                ]
                message = f"{'/'.join(path)} Property DeploymentConfiguration/DeploymentCircuitBreaker is missing."
                matches.append(RuleMatch(path, message))

            if not deployment_circuit_breaker.get("Enable") is True:
                path = [
                    "Resources",
                    resource_name,
                    "Properties",
                    "DeploymentConfiguration",
                    "DeploymentCircuitBreaker",
                    "Enable",
                ]
                message = f"{'/'.join(path)} Property DeploymentConfiguration/DeploymentCircuitBreaker/Enable should be true."
                matches.append(RuleMatch(path, message))

            if not deployment_circuit_breaker.get("Rollback") is False:
                path = [
                    "Resources",
                    resource_name,
                    "Properties",
                    "DeploymentConfiguration",
                    "DeploymentCircuitBreaker",
                    "Rollback",
                ]
                message = f"{'/'.join(path)} Property DeploymentConfiguration/DeploymentCircuitBreaker/Rollback should be false."
                matches.append(RuleMatch(path, message))

        return matches
