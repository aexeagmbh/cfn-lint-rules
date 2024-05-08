from logging import getLogger
from typing import List, Tuple, Type

import pytest
from cfnlint.rules import CloudFormationLintRule

from cfn_lint_ax.rules import (
    CertificateManagerCertificateNameTag,
    CloudfrontDistributionComment,
    CloudfrontDistributionLogging,
    CloudfrontDistributionResponseHeadersPolicy,
    CloudfrontResponseHeaderConfigLongHstsMaxAge,
    CodeBuildProjectCloudWatchLogs,
    CodeBuildProjectImage,
    CostAllocationTagProject,
    CostAllocationTags,
    EcrRepositoryAutocleanupTag,
    EcsServiceDeploymentConfiguration,
    EcsServiceFargatePlatformVersionNotOutdated,
    EcsServicePropagateTags,
    IntrinsicFunctionSubUnresolvedObject,
    MetadataAxChangesetAutoApprove,
    S3BucketEncryption,
    S3BucketPublicAccess,
    SqsQueueEncryption,
)
from tests.utils import BAD_TEMPLATE_FIXTURES_PATH, get_cnflint_errors

logger = getLogger(__name__)

ExpectedError = Tuple[int, Type[CloudFormationLintRule], str]


def test_all_rules_have_a_bad_test_template(
    ax_rule: CloudFormationLintRule, bad_templates: List[str]
) -> None:
    assert any(
        filename.startswith(f"{ax_rule.id}_") for filename in bad_templates
    ), f"No bad template test file for rule {ax_rule.__class__} ({ax_rule.id})"


test_parameters = (
    (
        "W9301_s3_bucket_with_bad_public_access_block_configuration.yaml",
        S3BucketPublicAccess,
        [
            (
                10,
                "Property Resources/TestBucket1/Properties/PublicAccessBlockConfiguration/BlockPublicPolicy is missing and should be true",
            ),
            (
                10,
                "Property Resources/TestBucket1/Properties/PublicAccessBlockConfiguration/IgnorePublicAcls is missing and should be true",
            ),
            (
                11,
                "Property Resources/TestBucket1/Properties/PublicAccessBlockConfiguration/BlockPublicAcls should be true",
            ),
            (
                30,
                "Property Resources/TestBucket2/Properties/PublicAccessBlockConfiguration/RestrictPublicBuckets is missing and should be true",
            ),
            (
                33,
                "Property Resources/TestBucket2/Properties/PublicAccessBlockConfiguration/IgnorePublicAcls should be true",
            ),
        ],
    ),
    (
        "W9301_s3_bucket_without_public_access_block_configuration.yaml",
        S3BucketPublicAccess,
        [
            (
                5,
                "Property Resources/TestBucket/Properties/PublicAccessBlockConfiguration is missing",
            )
        ],
    ),
    (
        "W9305_certificate_manager_certificate_without_name.yaml",
        CertificateManagerCertificateNameTag,
        [
            (
                7,
                "Property Resources/Certificate1/Properties/Tags is missing 'Name' tag",
            ),
            (
                18,
                "Property Resources/Certificate2/Properties/Tags is missing 'Name' tag",
            ),
        ],
    ),
    (
        "W9303_cloudfront_distribution_without_logging_configuration.yaml",
        CloudfrontDistributionLogging,
        [
            (
                6,
                "Property Resources/Distribution/Properties/DistributionConfig/Logging is missing",
            ),
        ],
    ),
    (
        "W9304_cloudfront_distribution_without_comment.yaml",
        CloudfrontDistributionComment,
        [
            (
                6,
                "Property Resources/Distribution/Properties/DistributionConfig/Comment is missing",
            ),
        ],
    ),
    (
        "W9307_cloudfront_distribution_without_response_header_policy.yaml",
        CloudfrontDistributionResponseHeadersPolicy,
        [
            (
                8,
                "Property Resources/Distribution/Properties/DistributionConfig/DefaultCacheBehavior/ResponseHeadersPolicyId is missing",
            ),
            (
                23,
                "Property ResponseHeadersPolicyId missing at Resources/Distribution/Properties/DistributionConfig/CacheBehaviors/1",
            ),
        ],
    ),
    (
        "W9308_cloudfront_response_header_policy_strict_transport_security.yaml",
        CloudfrontResponseHeaderConfigLongHstsMaxAge,
        [
            (
                3,
                "Property Resources/ResponseHeadersPolicy/ResponseHeadersPolicyConfig/SecurityHeadersConfig/StrictTransportSecurity/AccessControlMaxAgeSec should be an integer bigger or equal to 2 years (63072000).",
            ),
            (
                3,
                "Property Resources/ResponseHeadersPolicy/ResponseHeadersPolicyConfig/SecurityHeadersConfig/StrictTransportSecurity/Override should be true.",
            ),
            (
                19,
                "Property Resources/ResponseHeadersPolicyHstsOverrideDisabled/ResponseHeadersPolicyConfig/SecurityHeadersConfig/StrictTransportSecurity/Override should be true.",
            ),
            (
                29,
                "Property Resources/ResponseHeadersPolicyHstsMaxAgeToSmall/ResponseHeadersPolicyConfig/SecurityHeadersConfig/StrictTransportSecurity/AccessControlMaxAgeSec should be an integer bigger or equal to 2 years (63072000).",
            ),
            (
                39,
                "Property Resources/ResponseHeadersPolicyHstsAllBad/ResponseHeadersPolicyConfig/SecurityHeadersConfig/StrictTransportSecurity/AccessControlMaxAgeSec should be an integer bigger or equal to 2 years (63072000).",
            ),
            (
                39,
                "Property Resources/ResponseHeadersPolicyHstsAllBad/ResponseHeadersPolicyConfig/SecurityHeadersConfig/StrictTransportSecurity/Override should be true.",
            ),
        ],
    ),
    (
        "W9306_codebuild_project_cloudwatch_logs.yaml",
        CodeBuildProjectCloudWatchLogs,
        [
            (
                5,
                "Property Resources/Project1/Properties/LogsConfig/CloudWatchLogs/GroupName is missing. CodeBuild projects with cloudwatch logs enabled, should have a GroupName defined.",
            ),
            (
                38,
                "Property Resources/Project2/Properties/LogsConfig/CloudWatchLogs/GroupName is missing. CodeBuild projects with cloudwatch logs enabled, should have a GroupName defined.",
            ),
            (
                63,
                "Property Resources/Project3/Properties/LogsConfig/CloudWatchLogs/GroupName should be a Ref to a LogGroup.",
            ),
            (
                101,
                "Property Resources/Project4/Properties/LogsConfig/CloudWatchLogs/GroupName should be a Ref to a LogGroup.",
            ),
        ],
    ),
    (
        "I9301_ecs_fargate_platform_version_outdated.yaml",
        EcsServiceFargatePlatformVersionNotOutdated,
        [
            (
                10,
                "Resources/ECSService/Properties/PlatformVersion 1.3.0 is outdated. Set it to one of:  LATEST, 1.4.0",
            ),
        ],
    ),
    (
        "W9309_ecs_fargate_deployment_configuration.yaml",
        EcsServiceDeploymentConfiguration,
        [
            (
                5,
                "Resources/ECSService/Properties/DeploymentConfiguration Property DeploymentConfiguration is missing.",
            ),
            (
                5,
                "Resources/ECSService/Properties/DeploymentConfiguration/DeploymentCircuitBreaker Property DeploymentConfiguration/DeploymentCircuitBreaker is missing.",
            ),
            (
                5,
                "Resources/ECSService/Properties/DeploymentConfiguration/DeploymentCircuitBreaker/Enable Property DeploymentConfiguration/DeploymentCircuitBreaker/Enable should be true.",
            ),
            (
                5,
                "Resources/ECSService/Properties/DeploymentConfiguration/DeploymentCircuitBreaker/Rollback Property DeploymentConfiguration/DeploymentCircuitBreaker/Rollback should be false.",
            ),
            (
                30,
                "Resources/ECSServiceDeploymentCircuitBreakerWithBadValues/Properties/DeploymentConfiguration/DeploymentCircuitBreaker/Enable Property DeploymentConfiguration/DeploymentCircuitBreaker/Enable should be true.",
            ),
            (
                31,
                "Resources/ECSServiceDeploymentCircuitBreakerWithBadValues/Properties/DeploymentConfiguration/DeploymentCircuitBreaker/Rollback Property DeploymentConfiguration/DeploymentCircuitBreaker/Rollback should be false.",
            ),
        ],
    ),
    (
        "W9310_codebuild_project_image.yaml",
        CodeBuildProjectImage,
        [
            (
                25,
                "Property Resources/Project1/Properties/Environment/Image uses an AWS image other than standard.",
            ),
            (
                50,
                "Property Resources/Project2/Properties/Environment/Image uses an outdated version of the standard image.",
            ),
        ],
    ),
    (
        "E9401_metadata_ax_changeset_auto_approve.yaml",
        MetadataAxChangesetAutoApprove,
        [
            (
                4,
                "Metadata/AxChangesetAutoApprove/Add must be a list of strings.",
            ),
            (
                6,
                "Metadata/AxChangesetAutoApprove/ModifyConditionalReplacement[0] Bucket is not a resource type used in this template",
            ),
            (
                8,
                "Metadata/AxChangesetAutoApprove/ModifyReplacement must be a list of strings.",
            ),
            (
                10,
                "Metadata/AxChangesetAutoApprove/Remove[0] must be a string.",
            ),
            (
                11,
                "Metadata/AxChangesetAutoApprove/BadKey key BadKey is not allowed. Allowed keys for AxChangesetAutoApprove: Add, ModifyConditionalReplacement, ModifyReplacement, Remove.",
            ),
            (
                18,
                "Resources/TestBucket/Metadata/AxChangesetAutoApprove/ModifyConditionalReplacement must be a boolean.",
            ),
            (
                19,
                "Resources/TestBucket/Metadata/AxChangesetAutoApprove/ModifyReplacement must be a boolean.",
            ),
            (
                44,
                "Resources/TestQueue/Metadata/AxChangesetAutoApprove/ModifyReplacement must be a boolean.",
            ),
            (
                47,
                "Resources/TestQueue/Metadata/AxChangesetAutoApprove/BadKey key BadKey is not allowed. Allowed keys for AxChangesetAutoApprove: ModifyConditionalReplacement, ModifyReplacement.",
            ),
        ],
    ),
    (
        "W9302_s3_bucket_without_bucket_encryption.yaml",
        S3BucketEncryption,
        [
            (
                5,
                "Property Resources/TestBucket/Properties/BucketEncryption is missing",
            )
        ],
    ),
    (
        "E9101_unresolved_object.yaml",
        IntrinsicFunctionSubUnresolvedObject,
        [
            (
                21,
                "Sub contains an unresolved object",
            ),
            (
                38,
                "Sub contains an unresolved object",
            ),
        ],
    ),
    (
        "I9302_ecr_autocleanup_tag_missing.yaml",
        EcrRepositoryAutocleanupTag,
        [
            (
                6,
                "Resources/MyRepository/Properties/Tags is missing the 'autocleanup' tag.",
            ),
            (
                17,
                "Resources/MyRepository2/Properties/Tags is missing the 'autocleanup' tag.",
            ),
        ],
    ),
    (
        "I9302_ecr_autocleanup_tag_bad_value.yaml",
        EcrRepositoryAutocleanupTag,
        [
            (
                8,
                "Resources/MyRepository/Properties/Tags/0/Value value of the autocleanup tag mus be either 'true' or 'false'.",
            ),
            (
                21,
                "Resources/MyRepository2/Properties/Tags/0/Value value of the autocleanup tag mus be either 'true' or 'false'.",
            ),
            (
                34,
                "Resources/MyRepository3/Properties/Tags/0/Value value of the autocleanup tag mus be either 'true' or 'false'.",
            ),
            (
                47,
                "Resources/MyRepository4/Properties/Tags/0/Value value of the autocleanup tag mus be either 'true' or 'false'.",
            ),
            (
                60,
                "Resources/MyRepository5/Properties/Tags/0/Value value of the autocleanup tag mus be either 'true' or 'false'.",
            ),
        ],
    ),
    (
        "W9311_sqs_queue_encryption.yaml",
        SqsQueueEncryption,
        [
            (
                7,
                "Resource Resources/QueueWithOutEncryption/Properties Queue encryption must be enabled by either defining SqsManagedSseEnabled or KmsMasterKeyId.",
            ),
        ],
    ),
    (
        "I9303_cost_allocation_tags.yaml",
        CostAllocationTags,
        [
            (
                4,
                "Missing CostAllocationTag(s) Project, ProjectPart, ProjectPartDetail at Resources/FunctionWithoutAnyTagsRole/Properties/Tags",
            ),
            (
                4,
                "Missing CostAllocationTag(s) Project at Resources/FunctionWithBadCostAllocationTagsRole/Properties/Tags",
            ),
            (
                4,
                "Value of Tag ProjectPartDetail should be the resource id (FunctionWithBadCostAllocationTags, FunctionWithBadCostAllocationTagsRole) at Resources/FunctionWithBadCostAllocationTagsRole/Properties/Tags",
            ),
            (
                4,
                "Missing CostAllocationTag(s) Project, ProjectPart, ProjectPartDetail at Resources/ApiWithoutAnyTagsApiGatewayDefaultStage/Properties/Tags",
            ),
            (
                4,
                "Missing CostAllocationTag(s) Project at Resources/ApiWithBadCostAllocationTagsApiGatewayDefaultStage/Properties/Tags",
            ),
            (
                4,
                "Value of Tag ProjectPartDetail should be the resource id (ApiWithBadCostAllocationTags, ApiWithBadCostAllocationTagsApiGatewayDefaultStage) at Resources/ApiWithBadCostAllocationTagsApiGatewayDefaultStage/Properties/Tags",
            ),
            (
                9,
                "Missing CostAllocationTag(s) Project, ProjectPart, ProjectPartDetail at Resources/QueueWithoutAnyTags/Properties/Tags",
            ),
            (
                22,
                "Missing CostAllocationTag(s) Project, ProjectPart, ProjectPartDetail at Resources/QueueWithTagsButWithoutCostAllocationTags/Properties/Tags",
            ),
            (
                36,
                "Missing CostAllocationTag(s) Project at Resources/QueueWithoutProjectTag/Properties/Tags",
            ),
            (
                50,
                "Missing CostAllocationTag(s) Project at Resources/QueueWithoutProjectTag2/Properties/Tags",
            ),
            (
                66,
                "Missing CostAllocationTag(s) ProjectPart at Resources/QueueWithoutProjectPartTag/Properties/Tags",
            ),
            (
                80,
                "Missing CostAllocationTag(s) ProjectPart at Resources/QueueWithoutProjectPartTag2/Properties/Tags",
            ),
            (
                96,
                "Missing CostAllocationTag(s) ProjectPartDetail at Resources/QueueWithoutProjectPartDetailTag/Properties/Tags",
            ),
            (
                110,
                "Missing CostAllocationTag(s) ProjectPartDetail at Resources/QueueWithoutProjectPartDetailTag2/Properties/Tags",
            ),
            (
                126,
                "Value of Tag ProjectPart should be Ref to AWS::StackName ('ProjectPart: !Ref AWS::StackName') at Resources/QueueWithBadCostAllocationTagValues/Properties/Tags",
            ),
            (
                126,
                "Value of Tag ProjectPartDetail should be the resource id (QueueWithBadCostAllocationTagValues) at Resources/QueueWithBadCostAllocationTagValues/Properties/Tags",
            ),
            (
                142,
                "Value of Tag ProjectPart should be Ref to AWS::StackName ('ProjectPart: !Ref AWS::StackName') at Resources/QueueWithBadCostAllocationTagValues2/Properties/Tags",
            ),
            (
                142,
                "Value of Tag ProjectPartDetail should be the resource id (QueueWithBadCostAllocationTagValues2) at Resources/QueueWithBadCostAllocationTagValues2/Properties/Tags",
            ),
            (
                150,
                "Missing CostAllocationTag(s) Project, ProjectPart, ProjectPartDetail at Resources/ApiWithoutAnyTags/Properties/Tags",
            ),
            (
                153,
                "Missing CostAllocationTag(s) Project at Resources/ApiWithBadCostAllocationTags/Properties/Tags",
            ),
            (
                153,
                "Value of Tag ProjectPartDetail should be the resource id (ApiWithBadCostAllocationTags) at Resources/ApiWithBadCostAllocationTags/Properties/Tags",
            ),
            (
                161,
                "Missing CostAllocationTag(s) Project, ProjectPart, ProjectPartDetail at Resources/FunctionWithoutAnyTags/Properties/Tags",
            ),
            (
                167,
                "Missing CostAllocationTag(s) Project at Resources/FunctionWithBadCostAllocationTags/Properties/Tags",
            ),
            (
                167,
                "Value of Tag ProjectPartDetail should be the resource id (FunctionWithBadCostAllocationTags) at Resources/FunctionWithBadCostAllocationTags/Properties/Tags",
            ),
        ],
    ),
    (
        "I9304_cost_allocation_tags_project.yaml",
        CostAllocationTagProject,
        [
            (
                2,
                # "Multiple values of Project tag found: Bar ProjectCostAllocationTagExample, ProjectCostAllocationTagExample, ProjectCostAllocationTagExampleFoo, SomethingElse. All resources in a stack should have the same value for the Project tag.",
                "Multiple values of Project tag found: Bar ProjectCostAllocationTagExample, ProjectCostAllocationTagExample, ProjectCostAllocationTagExampleFoo, SomethingElse. All resources in a stack should have the same value for the Project tag.",
            ),
        ],
    ),
    (
        "I9305_ecs_service_propagate_tags.yaml",
        EcsServicePropagateTags,
        [
            (
                5,
                'PropagateTags should have the value "SERVICE" at Resources/ECSServiceWithoutPropagateTags/Properties/PropagateTags',
            ),
            (
                36,
                'PropagateTags should have the value "SERVICE" at Resources/ECSServiceWithWrongPropagateTagsValue/Properties/PropagateTags',
            ),
        ],
    ),
)


@pytest.mark.parametrize("filename,rule_class,expected_errors", test_parameters)
def test_bad(
    filename: str,
    rule_class: CloudFormationLintRule,
    expected_errors: List[Tuple[int, str]],
) -> None:
    filename = (BAD_TEMPLATE_FIXTURES_PATH / filename).as_posix()

    errs = get_cnflint_errors(template_path=filename)

    lint_rule_class_name = f"{rule_class.__module__}.{rule_class.__name__}"
    if lint_rule_class_name.startswith("rules."):
        lint_rule_class_name = lint_rule_class_name[len("rules.") :]

    for expected_error in expected_errors:
        line_number = expected_error[0]
        message = expected_error[1]

        for errs_idx, match in enumerate(errs):
            match_rule_class = match.rule.__class__
            match_rule_class_name = (
                f"{match_rule_class.__module__}.{match_rule_class.__name__}"
            )
            print(match.linenumber)
            print(match_rule_class_name)
            print(match.message)
            if (
                match.linenumber == line_number
                and match_rule_class_name == lint_rule_class_name
                and match.message == message
            ):
                del errs[errs_idx]
                break
        else:
            assert False, f"{line_number} - {rule_class} - {message} not in errs"

    for err in errs:
        logger.warning(err)
    assert len(errs) == 0, errs


def test_bad_template_is_in_test_parameter(bad_template: str) -> None:
    assert any(
        paramters[0] == bad_template for paramters in test_parameters
    ), f"{bad_template} is missing in the list 'test_parameters'"


def test_all_test_paramters_have_at_least_one_expected_error() -> None:
    for n, parameters in enumerate(test_parameters):
        assert (
            len(parameters[2]) > 0
        ), f"test_paramter[{n}] ({parameters[0]}) has no expected errors"
