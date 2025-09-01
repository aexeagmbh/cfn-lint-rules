"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from logging import getLogger
from typing import Any, TypedDict

from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.schema import PROVIDER_SCHEMA_MANAGER
from cfnlint.template import Template

LOGGER = getLogger(__name__)


class TagObject(TypedDict):
    Key: str | dict[str, Any]
    Value: str | dict[str, Any]


class _CostAllocationTagBase(CloudFormationLintRule):  # type: ignore[misc]
    def has_tags(self, resource_obj: dict) -> bool:  # type: ignore[type-arg]
        if "Tags" in resource_obj.get("Properties", {}):
            return True
        if resource_obj.get("Type") == "AWS::ApiGatewayV2::Api":
            if "tags" in resource_obj.get("Properties", {}).get("Body", {}):
                return True
        return False

    def get_tags(self, resource_obj: dict) -> list[TagObject]:  # type: ignore[type-arg]
        if not self.has_tags(resource_obj):
            return []
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
            return []

        if isinstance(tags, dict):
            # tags_as_dict = tags
            return [{"Key": k, "Value": v} for k, v in tags.items()]
        if isinstance(tags, list):
            # tags_as_dict = {d["Key"]: d["Value"] for d in tags}
            return tags
        raise ValueError(f"Tags should be a list or a dict, but it is {tags}")


class CostAllocationTags(_CostAllocationTagBase):
    """Check if Tags are included on supported resources"""

    id = "I9303"
    shortdesc = "Cost Allocation Tags"
    description = (
        "Check Cost Allocation Tags are included on resources that support it."
    )
    tags = ["resources", "tags"]

    def expeted_detail_tag_values(  # pylint: disable=too-many-return-statements
        self, resource_name: str, resource_obj: dict[str, object], cfn: Template
    ) -> set[str]:
        if cfn.has_serverless_transform():
            if resource_obj.get("Type") == "AWS::IAM::Role" and resource_name.endswith(
                "Role"
            ):

                possible_serverless_function_id = resource_name.removesuffix("Role")
                serverless_resources = cfn.get_resources(
                    ["AWS::Lambda::Function", "AWS::StepFunctions::StateMachine"]
                )
                if possible_serverless_function_id in serverless_resources:
                    return {possible_serverless_function_id, resource_name}
            if resource_obj.get("Type") == "AWS::ApiGatewayV2::Stage":
                if resource_name.endswith("ApiGatewayDefaultStage"):
                    possible_serverless_httpapi_id = resource_name.removesuffix(
                        "ApiGatewayDefaultStage"
                    )
                    if possible_serverless_httpapi_id == "":
                        possible_serverless_httpapi_id = "Api"
                    httpapi_resources = cfn.get_resources("AWS::ApiGatewayV2::Api")
                    if possible_serverless_httpapi_id in httpapi_resources:
                        return {possible_serverless_httpapi_id, resource_name}
                else:
                    httpapi_resources = cfn.get_resources("AWS::ApiGatewayV2::Api")
                    possible_httpapi_resources_id = {
                        k
                        for k in httpapi_resources.keys()
                        if resource_name.startswith(k)
                    }
                    return {resource_name}.union(possible_httpapi_resources_id)
            if resource_obj.get(
                "Type"
            ) == "AWS::ApiGatewayV2::DomainName" and resource_name.startswith(
                "ApiGatewayDomainName"
            ):
                httpapi_resources = cfn.get_resources("AWS::ApiGatewayV2::Api")
                return {resource_name}.union(httpapi_resources.keys())
            if resource_obj.get("Type") == "AWS::ApiGateway::Stage":
                httpapi_resources = cfn.get_resources("AWS::ApiGateway::RestApi")
                possible_httpapi_resources_id = {
                    k for k in httpapi_resources.keys() if resource_name.startswith(k)
                }
                return {resource_name}.union(possible_httpapi_resources_id)
            if resource_obj.get(
                "Type"
            ) == "AWS::ApiGateway::DomainName" and resource_name.startswith(
                "ApiGatewayDomainName"
            ):
                restapi_resources = cfn.get_resources("AWS::ApiGateway::RestApi")
                return {resource_name}.union(restapi_resources.keys())

        return {resource_name}

    def match(  # pylint: disable=too-many-locals
        self, cfn: Template
    ) -> list[RuleMatch]:
        """Check Tags for required keys"""

        matches = []

        resources = cfn.get_resources()
        for resource_name, resource_obj in resources.items():
            if not any(
                "Tags" in schema.schema["properties"]
                for (
                    _region,
                    schema,
                ) in PROVIDER_SCHEMA_MANAGER.get_resource_schemas_by_regions(
                    resource_obj.get("Type", ""), cfn.regions
                )
            ):
                continue

            path = ["Resources", resource_name, "Properties", "Tags"]

            tags_as_list = self.get_tags(resource_obj)

            def _get_tag_value(key: str) -> str | dict[str, Any]:
                for tag in tags_as_list:  # pylint: disable=cell-var-from-loop
                    if tag["Key"] == key:
                        return tag["Value"]
                raise ValueError(f"Tag {key} not found")

            def _is_tag_present(key: str) -> bool:
                for tag in tags_as_list:  # pylint: disable=cell-var-from-loop
                    if tag["Key"] == key:
                        return True
                return False

            missing_tags = []
            for required_tag in ["Project", "ProjectPart", "ProjectPartDetail"]:
                if not _is_tag_present(required_tag):
                    missing_tags.append(required_tag)
            if missing_tags and not (
                cfn.has_serverless_transform()
                and (
                    resource_obj.get("Type")
                    in {
                        "AWS::CodeDeploy::Application",
                        "AWS::CodeDeploy::DeploymentGroup",
                        "AWS::Lambda::EventSourceMapping",
                    }
                    or (
                        resource_obj.get("Type") == "AWS::Events::Rule"
                        and isinstance(
                            targets := resource_obj.get("Properties", {}).get(
                                "Targets"
                            ),
                            list,
                        )
                        and len(targets) == 1
                        and resources.get(
                            targets[0].get("Arn", {}).get("Ref", ""), {}
                        ).get("Type", "")
                        == "AWS::Lambda::Alias"
                    )
                )
            ):
                message = f"Missing CostAllocationTag(s) {', '.join(missing_tags)} at {'/'.join(path)}"
                matches.append(RuleMatch(path, message))

            if _is_tag_present("ProjectPart"):
                if not _get_tag_value("ProjectPart") == {"Ref": "AWS::StackName"}:
                    matches.append(
                        RuleMatch(
                            path,
                            f"Value of Tag ProjectPart should be Ref to AWS::StackName ('ProjectPart: !Ref AWS::StackName') at {'/'.join(path)}",
                        )
                    )
            if _is_tag_present("ProjectPartDetail"):
                expected_values = self.expeted_detail_tag_values(
                    resource_name, resource_obj, cfn
                )
                project_part_detail_value = _get_tag_value("ProjectPartDetail")
                if (
                    not isinstance(project_part_detail_value, str)
                    or project_part_detail_value not in expected_values
                ):
                    matches.append(
                        RuleMatch(
                            path,
                            f"Value of Tag ProjectPartDetail should be the resource id ({', '.join(sorted(expected_values))}) at {'/'.join(path)}",
                        )
                    )

        return matches


class CostAllocationTagProject(_CostAllocationTagBase):
    """Check if Tags are included on supported resources"""

    id = "I9304"
    shortdesc = "Project Cost Allocation Tag"
    description = (
        "Check that all resources have the same Cost Allocation Tag Project value."
    )
    tags = ["resources", "tags"]

    def match(  # pylint: disable=too-many-locals
        self, cfn: Template
    ) -> list[RuleMatch]:
        """Check Tags for required keys"""

        matches = []

        resources = cfn.get_resources()
        seen_values_of_project_tag = set()
        for resource_obj in resources.values():
            if not any(
                "Tags" in schema.schema["properties"]
                for (
                    _region,
                    schema,
                ) in PROVIDER_SCHEMA_MANAGER.get_resource_schemas_by_regions(
                    resource_obj.get("Type", ""), cfn.regions
                )
            ):
                continue

            tags_as_list = self.get_tags(resource_obj)

            def _get_tag_value(key: str) -> str | dict[str, Any]:
                for tag in tags_as_list:  # pylint: disable=cell-var-from-loop
                    if tag["Key"] == key:
                        return tag["Value"]
                raise ValueError(f"Tag {key} not found")

            def _is_tag_present(key: str) -> bool:
                for tag in tags_as_list:  # pylint: disable=cell-var-from-loop
                    if tag["Key"] == key:
                        return True
                return False

            if _is_tag_present("Project"):
                seen_values_of_project_tag.add(_get_tag_value("Project"))

        if len(seen_values_of_project_tag) > 1:
            matches.append(
                RuleMatch(
                    ["Resources"],
                    f"Multiple values of Project tag found: {', '.join(sorted(str(v) for v in seen_values_of_project_tag))}. All resources in a stack should have the same value for the Project tag.",
                )
            )
        return matches


class EcsServicePropagateTags(CloudFormationLintRule):  # type: ignore[misc]
    id = "I9305"
    shortdesc = "ECS Service PropagateTags should be SERVICE"
    description = "Check that ECS Service PropagateTags is set to SERVICE to propagate tags to tasks."
    tags = ["resources", "ecs", "tags"]

    def match(self, cfn: Template) -> list[RuleMatch]:
        matches = []

        resources = cfn.get_resources()
        for resource_name, resource_obj in resources.items():
            resource_type = resource_obj.get("Type", "")
            if resource_type != "AWS::ECS::Service":
                continue

            path = ["Resources", resource_name, "Properties", "PropagateTags"]

            if resource_obj.get("Properties", {}).get("PropagateTags") != "SERVICE":
                matches.append(
                    RuleMatch(
                        path,
                        f'PropagateTags should have the value "SERVICE" at {"/".join(path)}',
                    )
                )

        return matches
