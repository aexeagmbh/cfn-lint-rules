"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from logging import getLogger

import cfnlint.helpers
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template

LOGGER = getLogger(__name__)


class CostAllocationTags(CloudFormationLintRule):  # type: ignore[misc]
    """Check if Tags are included on supported resources"""

    id = "I9303"
    shortdesc = "Tags are included on resources that support it"
    description = "Check Tags for resources"
    tags = ["resources", "tags"]
    experimental = True

    def get_resources_with_tags(self, region: str) -> list[str]:
        """Get resource types that support tags"""
        resourcespecs = cfnlint.helpers.RESOURCE_SPECS[region]
        resourcetypes = resourcespecs["ResourceTypes"]

        matches = []
        for resourcetype, resourceobj in resourcetypes.items():
            propertiesobj = resourceobj.get("Properties")
            if propertiesobj:
                if "Tags" in propertiesobj:
                    matches.append(resourcetype)

        return matches

    def expeted_detail_tag_values(
        self, resource_name: str, resource_obj: dict[str, object], cfn: Template
    ) -> set[str]:
        if cfn.has_serverless_transform():
            if resource_obj.get("Type") == "AWS::IAM::Role" and resource_name.endswith(
                "Role"
            ):
                possible_serverless_function_id = resource_name.removesuffix("Role")
                # function_resources = cfn.get_resources("AWS::Serverless::Function")
                function_resources = cfn.get_resources("AWS::Lambda::Function")
                if possible_serverless_function_id in function_resources:
                    return {possible_serverless_function_id, resource_name}
            if resource_obj.get(
                "Type"
            ) == "AWS::ApiGatewayV2::Stage" and resource_name.endswith(
                "ApiGatewayDefaultStage"
            ):
                possible_serverless_httpapi_id = resource_name.removesuffix(
                    "ApiGatewayDefaultStage"
                )
                if possible_serverless_httpapi_id == "":
                    possible_serverless_httpapi_id = "Api"
                httpapi_resources = cfn.get_resources("AWS::ApiGatewayV2::Api")
                if possible_serverless_httpapi_id in httpapi_resources:
                    return {possible_serverless_httpapi_id, resource_name}
            if resource_obj.get(
                "Type"
            ) == "AWS::ApiGatewayV2::DomainName" and resource_name.startswith(
                "ApiGatewayDomainName"
            ):
                httpapi_resources = cfn.get_resources("AWS::ApiGatewayV2::Api")
                return {resource_name}.union(httpapi_resources.keys())

        return {resource_name}

    def has_tags(self, resource_obj: dict) -> bool:  # type: ignore[type-arg]
        if "Tags" in resource_obj.get("Properties", {}):
            return True
        if resource_obj.get("Type") == "AWS::ApiGatewayV2::Api":
            if "tags" in resource_obj.get("Properties", {}).get("Body"):
                return True
        return False

    def get_tags(self, resource_obj: dict) -> dict[str, str]:  # type: ignore[type-arg]
        if not self.has_tags(resource_obj):
            return {}
        resource_properties = resource_obj.get("Properties", {})
        if resource_obj.get("Type") == "AWS::ApiGatewayV2::Api":
            tags = resource_properties.get("Tags")
            if not tags:
                tags = resource_properties.get("Body", {}).get("tags")
                tags = {
                    d["name"]: d["x-amazon-apigateway-tag-value"]
                    for d in tags
                    if "name" in d and "x-amazon-apigateway-tag-value" in d
                }
        else:
            tags = resource_properties["Tags"]

        if not tags:
            return {}

        if isinstance(tags, dict):
            tags_as_dict = tags
        elif isinstance(tags, list):
            tags_as_dict = {d["Key"]: d["Value"] for d in tags}
        else:
            raise ValueError(f"Tags should be a list or a dict, but it is {tags}")

        return tags_as_dict

    def match(self, cfn: Template) -> list[RuleMatch]:
        """Check Tags for required keys"""

        matches = []

        resources_tags = self.get_resources_with_tags(cfn.regions[0])
        resources = cfn.get_resources()
        seen_values_of_project_tag = set()
        for resource_name, resource_obj in resources.items():
            resource_type = resource_obj.get("Type", "")
            if resource_type not in resources_tags:
                continue

            path = ["Resources", resource_name, "Properties", "Tags"]

            tags_as_dict = self.get_tags(resource_obj)

            missing_tags = []
            for required_tag in ["Project", "ProjectPart", "ProjectPartDetail"]:
                if required_tag not in tags_as_dict:
                    missing_tags.append(required_tag)
            if missing_tags:
                message = f"Missing CostAllocationTag(s) {', '.join(missing_tags)} at {'/'.join(path)}"
                matches.append(RuleMatch(path, message))

            if "ProjectPart" in tags_as_dict:
                if not tags_as_dict["ProjectPart"] == {"Ref": "AWS::StackName"}:
                    matches.append(
                        RuleMatch(
                            path,
                            f"Value of Tag ProjectPart should be Ref to AWS::StackName ('ProjectPart: !Ref AWS::StackName') at {'/'.join(path)}",
                        )
                    )
            if "ProjectPartDetail" in tags_as_dict:
                expected_values = self.expeted_detail_tag_values(
                    resource_name, resource_obj, cfn
                )
                if (
                    not isinstance(tags_as_dict["ProjectPartDetail"], str)
                    or tags_as_dict["ProjectPartDetail"] not in expected_values
                ):
                    matches.append(
                        RuleMatch(
                            path,
                            f"Value of Tag ProjectPartDetail should be the resource id ({', '.join(sorted(expected_values))}) at {'/'.join(path)}",
                        )
                    )

            if "Project" in tags_as_dict:
                seen_values_of_project_tag.add(tags_as_dict["Project"])
        if len(seen_values_of_project_tag) > 1:
            matches.append(
                RuleMatch(
                    ["Resources"],
                    f"Multiple values of Project tag found: {', '.join(sorted(seen_values_of_project_tag))}. All resources in a stack should have the same value for the Project tag.",
                )
            )
        return matches
