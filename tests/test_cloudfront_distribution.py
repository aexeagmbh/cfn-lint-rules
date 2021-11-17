from typing import List

import pytest

from cfn_lint_ax.rules import (
    CloudfrontDistributionComment,
    CloudfrontDistributionLogging,
)
from cfn_lint_ax.rules.cloud_front import (
    CloudfrontDistributionResponseHeadersPolicy,
    CloudfrontResponseHeaderConfigLongHstsMaxAge,
)
from tests.utils import BAD_TEMPLATE_FIXTURES_PATH, ExpectedError, assert_all_matches


@pytest.mark.parametrize(
    "filename,expected_errors",
    [
        (
            "cloudfront_distribution_without_logging_configuration.yaml",
            [
                (
                    6,
                    CloudfrontDistributionLogging,
                    "Property Resources/Distribution/Properties/DistributionConfig/Logging is missing",
                ),
            ],
        ),
        (
            "cloudfront_distribution_without_comment.yaml",
            [
                (
                    6,
                    CloudfrontDistributionComment,
                    "Property Resources/Distribution/Properties/DistributionConfig/Comment is missing",
                ),
            ],
        ),
        (
            "cloudfront_distribution_without_response_header_policy.yaml",
            [
                (
                    8,
                    CloudfrontDistributionResponseHeadersPolicy,
                    "Property Resources/Distribution/Properties/DistributionConfig/DefaultCacheBehavior/ResponseHeadersPolicyId is missing",
                ),
                (
                    23,
                    CloudfrontDistributionResponseHeadersPolicy,
                    "Property ResponseHeadersPolicyId missing at Resources/Distribution/Properties/DistributionConfig/CacheBehaviors/1",
                ),
            ],
        ),
        (
            "cloudfront_response_header_policy_strict_transport_security.yaml",
            [
                (
                    3,
                    CloudfrontResponseHeaderConfigLongHstsMaxAge,
                    "Property Resources/ResponseHeadersPolicy/ResponseHeadersPolicyConfig/SecurityHeadersConfig/StrictTransportSecurity/AccessControlMaxAgeSec should be an integer bigger or equal to 2 years (63072000).",
                ),
                (
                    3,
                    CloudfrontResponseHeaderConfigLongHstsMaxAge,
                    "Property Resources/ResponseHeadersPolicy/ResponseHeadersPolicyConfig/SecurityHeadersConfig/StrictTransportSecurity/Override should be true.",
                ),
                (
                    19,
                    CloudfrontResponseHeaderConfigLongHstsMaxAge,
                    "Property Resources/ResponseHeadersPolicyHstsOverrideDisabled/ResponseHeadersPolicyConfig/SecurityHeadersConfig/StrictTransportSecurity/Override should be true.",
                ),
                (
                    29,
                    CloudfrontResponseHeaderConfigLongHstsMaxAge,
                    "Property Resources/ResponseHeadersPolicyHstsMaxAgeToSmall/ResponseHeadersPolicyConfig/SecurityHeadersConfig/StrictTransportSecurity/AccessControlMaxAgeSec should be an integer bigger or equal to 2 years (63072000).",
                ),
                (
                    39,
                    CloudfrontResponseHeaderConfigLongHstsMaxAge,
                    "Property Resources/ResponseHeadersPolicyHstsAllBad/ResponseHeadersPolicyConfig/SecurityHeadersConfig/StrictTransportSecurity/AccessControlMaxAgeSec should be an integer bigger or equal to 2 years (63072000).",
                ),
                (
                    39,
                    CloudfrontResponseHeaderConfigLongHstsMaxAge,
                    "Property Resources/ResponseHeadersPolicyHstsAllBad/ResponseHeadersPolicyConfig/SecurityHeadersConfig/StrictTransportSecurity/Override should be true.",
                ),
            ],
        ),
    ],
)
def test_bad_cloudfront_distribution_config(
    filename: str, expected_errors: List[ExpectedError]
) -> None:
    filename = (BAD_TEMPLATE_FIXTURES_PATH / filename).as_posix()

    assert_all_matches(filename, expected_errors)
