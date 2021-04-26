from typing import List

from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class CertificateManagerCertificateNameTag(CloudFormationLintRule):  # type: ignore[misc]
    """Rule description"""

    id = "W9305"
    shortdesc = "Tag Certificate With Name"
    description = "Tag Certificate With Name"
    tags = ["acm", "CertificateManager", "naming", "tag"]

    def match(self, cfn: Template) -> List[RuleMatch]:
        matches = []

        resources = cfn.get_resources(["AWS::CertificateManager::Certificate"])
        for resource_name, resource in resources.items():
            properties = resource.get("Properties", {})
            tags = properties.get("Tags", [])

            path = [
                "Resources",
                resource_name,
                "Properties",
                "Tags",
            ]
            for tag in tags:
                if tag.get("Key") == "Name":
                    break
            else:
                message = f"Property {'/'.join(path)} is missing 'Name' tag"
                matches.append(RuleMatch(path, message))

        return matches
