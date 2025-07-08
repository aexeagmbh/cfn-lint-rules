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


class CloudfrontDistributionResponseHeadersPolicy(CloudFormationLintRule):  # type: ignore[misc]
    """Rule description"""

    id = "W9307"
    shortdesc = "Configure Cloudfront Distribution ResponseHeadersPolicy"
    description = "Configure Cloudfront Distribution ResponseHeadersPolicy"
    source_url = "https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/understanding-response-headers-policies.html"
    tags = ["cloudfront", "headers"]

    def match(self, cfn: Template) -> List[RuleMatch]:
        matches = []

        resources = cfn.get_resources(["AWS::CloudFront::Distribution"])
        for resource_name, resource in resources.items():
            properties = resource.get("Properties", {})
            default_cache_behavior = properties.get("DistributionConfig", {}).get(
                "DefaultCacheBehavior", {}
            )

            path = [
                "Resources",
                resource_name,
                "Properties",
                "DistributionConfig",
                "DefaultCacheBehavior",
            ]
            if not default_cache_behavior.get("ResponseHeadersPolicyId"):
                message = (
                    f"Property {'/'.join(path)}/ResponseHeadersPolicyId is missing"
                )
                matches.append(RuleMatch(path, message))

            for index, cache_behavior in enumerate(
                properties.get("DistributionConfig", {}).get("CacheBehaviors", [])
            ):
                path = [
                    "Resources",
                    resource_name,
                    "Properties",
                    "DistributionConfig",
                    "CacheBehaviors",
                    index,
                ]
                if not cache_behavior.get("ResponseHeadersPolicyId"):
                    message = f"Property ResponseHeadersPolicyId missing at {'/'.join([str(p) for p in path])}"
                    matches.append(RuleMatch(path, message))

        return matches


class CloudfrontResponseHeaderConfigLongHstsMaxAge(CloudFormationLintRule):  # type: ignore[misc]
    """Rule description"""

    id = "W9308"
    shortdesc = "Configure Cloudfront ResponseHeadersConfig long hsts max-age"
    description = "Configure Cloudfront ResponseHeadersConfig long hsts max-age"
    source_url = "https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/understanding-response-headers-policies.html"
    tags = ["cloudfront", "headers", "hsts", "Strict Transport Security"]

    def match(self, cfn: Template) -> List[RuleMatch]:
        matches = []

        resources = cfn.get_resources(["AWS::CloudFront::ResponseHeadersPolicy"])
        for resource_name, resource in resources.items():
            properties = resource.get("Properties", {})
            strict_transpost_security = (
                properties.get("ResponseHeadersPolicyConfig", {})
                .get("SecurityHeadersConfig", {})
                .get("StrictTransportSecurity", {})
            )

            two_years = 2 * 365 * 24 * 60 * 60
            # strict_transpost_security.get("AccessControlMaxAgeSec") >= two_years

            path = [
                "Resources",
                resource_name,
                "ResponseHeadersPolicyConfig",
                "SecurityHeadersConfig",
                "StrictTransportSecurity",
                "AccessControlMaxAgeSec",
            ]
            access_control_max_age_sec = strict_transpost_security.get(
                "AccessControlMaxAgeSec"
            )
            if (
                not isinstance(access_control_max_age_sec, int)
                or not access_control_max_age_sec >= two_years
            ):
                message = f"Property {'/'.join(path)} should be an integer bigger or equal to 2 years ({two_years})."
                matches.append(RuleMatch(path, message))

            path = [
                "Resources",
                resource_name,
                "ResponseHeadersPolicyConfig",
                "SecurityHeadersConfig",
                "StrictTransportSecurity",
                "Override",
            ]
            if strict_transpost_security.get("Override") is not True:
                message = f"Property {'/'.join(path)} should be true."
                matches.append(RuleMatch(path, message))

        return matches
