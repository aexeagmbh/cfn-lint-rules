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
    EcrRepositoryAutocleanupTag,
    EcsServiceDeploymentConfiguration,
    EcsServiceFargatePlatformVersionNotOutdated,
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
                23,
                "Property Resources/TestBucket2/Properties/PublicAccessBlockConfiguration/RestrictPublicBuckets is missing and should be true",
            ),
            (
                26,
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
                5,
                "Property Resources/Certificate1/Properties/Tags is missing 'Name' tag",
            ),
            (
                11,
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
                31,
                "Property Resources/Project2/Properties/LogsConfig/CloudWatchLogs/GroupName is missing. CodeBuild projects with cloudwatch logs enabled, should have a GroupName defined.",
            ),
            (
                49,
                "Property Resources/Project3/Properties/LogsConfig/CloudWatchLogs/GroupName should be a Ref to a LogGroup.",
            ),
            (
                72,
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
                22,
                "Resources/ECSServiceDeploymentCircuitBreakerWithBadValues/Properties/DeploymentConfiguration/DeploymentCircuitBreaker/Enable Property DeploymentConfiguration/DeploymentCircuitBreaker/Enable should be true.",
            ),
            (
                23,
                "Resources/ECSServiceDeploymentCircuitBreakerWithBadValues/Properties/DeploymentConfiguration/DeploymentCircuitBreaker/Rollback Property DeploymentConfiguration/DeploymentCircuitBreaker/Rollback should be false.",
            ),
        ],
    ),
    (
        "W9310_codebuild_project_image.yaml",
        CodeBuildProjectImage,
        [
            (
                17,
                "Property Resources/Project1/Properties/Environment/Image uses an AWS image other than standard.",
            ),
            (
                35,
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
                37,
                "Resources/TestQueue/Metadata/AxChangesetAutoApprove/ModifyReplacement must be a boolean.",
            ),
            (
                40,
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
                31,
                "Sub contains an unresolved object",
            ),
        ],
    ),
    (
        "I9302_ecr_autocleanup_tag_missing.yaml",
        EcrRepositoryAutocleanupTag,
        [
            (
                3,
                "Resources/MyRepository/Properties/Tags is missing the 'autocleanup' tag.",
            ),
            (
                9,
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
                15,
                "Resources/MyRepository2/Properties/Tags/0/Value value of the autocleanup tag mus be either 'true' or 'false'.",
            ),
            (
                22,
                "Resources/MyRepository3/Properties/Tags/0/Value value of the autocleanup tag mus be either 'true' or 'false'.",
            ),
            (
                29,
                "Resources/MyRepository4/Properties/Tags/0/Value value of the autocleanup tag mus be either 'true' or 'false'.",
            ),
            (
                36,
                "Resources/MyRepository5/Properties/Tags/0/Value value of the autocleanup tag mus be either 'true' or 'false'.",
            ),
        ],
    ),
    (
        "W9311_sqs_queue_encryption.yaml",
        SqsQueueEncryption,
        [
            (
                3,
                "Resource Resources/QueueWithOutEncryption/Properties Queue encryption must be enabled by either defining SqsManagedSseEnabled or KmsMasterKeyId.",
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
