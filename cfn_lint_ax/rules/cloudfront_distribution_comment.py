from typing import List

from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class CloudfrontDistributionComment(CloudFormationLintRule):  # type: ignore[misc]
    """Rule description"""

    id = "W9304"
    shortdesc = "Enable Cloudfront Distribution Comment"
    description = "Enable Cloudfront Distribution Comment"
    tags = ["cloudfront"]

    def match(self, cfn: Template) -> List[RuleMatch]:
        matches = []

        resources = cfn.get_resources(["AWS::CloudFront::Distribution"])
        for resource_name, resource in resources.items():
            properties = resource.get("Properties", {})
            comment = properties.get("DistributionConfig", {}).get("Comment")

            path = [
                "Resources",
                resource_name,
                "Properties",
                "DistributionConfig",
                "Comment",
            ]
            if not comment:
                message = f"Property {'/'.join(path)} is missing"
                matches.append(RuleMatch(path, message))

        return matches
