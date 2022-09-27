from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class EcrRepositoryAutocleanupTag(CloudFormationLintRule):  # type: ignore[misc]
    """Rule description"""

    id = "I9302"
    shortdesc = "Ecr repositories should have an autocleanup tag."
    description = "Ecr repositories should have an autocleanup tag with either the value 'true' or 'false'."
    tags = ["ecr"]

    def match(self, cfn: Template) -> list[RuleMatch]:
        matches = []

        resources = cfn.get_resources(["AWS::ECR::Repository"])
        for resource_name, resource in resources.items():
            properties = resource.get("Properties", {})
            tags = properties.get("Tags", [])
            autocleanup_tag_present = False
            for ctr, tag in enumerate(tags):
                if tag["Key"] == "autocleanup":
                    autocleanup_tag_present = True
                    if tag["Value"] not in {"true", "false"}:
                        path = [
                            "Resources",
                            resource_name,
                            "Properties",
                            "Tags",
                            ctr,
                            "Value",
                        ]
                        message = f"{'/'.join(str(p) for p in path)} value of the autocleanup tag mus be either 'true' or 'false'."
                        matches.append(RuleMatch(path, message))

            if not autocleanup_tag_present:
                path = ["Resources", resource_name, "Properties", "Tags"]
                message = f"{'/'.join(path)} is missing the 'autocleanup' tag."
                matches.append(RuleMatch(path, message))

        return matches
