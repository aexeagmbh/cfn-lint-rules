from typing import List

from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class CloudfrontDistributionLogging(CloudFormationLintRule):  # type: ignore[misc]
    """Rule description"""

    id = "W9303"
    shortdesc = "Enable Cloudfront Distribution Logging"
    description = "Enable Cloudfront Distribution Logging"
    source_url = "https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/AccessLogs.html"
    tags = ["cloudfront", "logging"]

    def match(self, cfn: Template) -> List[RuleMatch]:
        matches = []

        resources = cfn.get_resources(["AWS::CloudFront::Distribution"])
        for resource_name, resource in resources.items():
            properties = resource.get("Properties", {})
            logging = properties.get("DistributionConfig", {}).get("Logging")

            path = [
                "Resources",
                resource_name,
                "Properties",
                "DistributionConfig",
                "Logging",
            ]
            if not logging:
                message = f"Property {'/'.join(path)} is missing"
                matches.append(RuleMatch(path, message))

        return matches
