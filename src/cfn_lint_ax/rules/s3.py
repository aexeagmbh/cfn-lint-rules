from typing import List

from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class S3BucketEncryption(CloudFormationLintRule):  # type: ignore[misc]
    """Rule description"""

    id = "W9302"
    shortdesc = "Configure S3 Server-Side Encryption"
    description = "Configure S3 Server-Side Encryption with AES256 or aws:kms."
    source_url = (
        "https://docs.aws.amazon.com/AmazonS3/latest/dev/serv-side-encryption.html"
    )
    tags = ["s3", "security"]

    def match(self, cfn: Template) -> List[RuleMatch]:
        matches = []

        resources = cfn.get_resources(["AWS::S3::Bucket"])
        for resource_name, resource in resources.items():
            properties = resource.get("Properties", {})
            if "BucketEncryption" not in properties:
                path = ["Resources", resource_name, "Properties", "BucketEncryption"]
                message = f"Property {'/'.join(path)} is missing"
                matches.append(RuleMatch(path, message))

        return matches


class S3BucketPublicAccess(CloudFormationLintRule):  # type: ignore[misc]
    """Rule description"""

    id = "W9301"
    shortdesc = "Enable S3 Block Public Access"
    description = "Enable S3 Block Public Access"
    source_url = "https://aws.amazon.com/about-aws/whats-new/2018/11/introducing-amazon-s3-block-public-access/"
    tags = ["s3", "security"]

    def match(self, cfn: Template) -> List[RuleMatch]:
        matches = []

        resources = cfn.get_resources(["AWS::S3::Bucket"])
        for resource_name, resource in resources.items():
            properties = resource.get("Properties", {})
            public_access_block_configuration = properties.get(
                "PublicAccessBlockConfiguration"
            )
            path = [
                "Resources",
                resource_name,
                "Properties",
                "PublicAccessBlockConfiguration",
            ]
            if not public_access_block_configuration:
                message = f"Property {'/'.join(path)} is missing"
                matches.append(RuleMatch(path, message))
                continue
            for key in [
                "BlockPublicAcls",
                "BlockPublicPolicy",
                "IgnorePublicAcls",
                "RestrictPublicBuckets",
            ]:
                value = public_access_block_configuration.get(key)
                if value is None:
                    detail_path = path + [key]
                    message = f"Property {'/'.join(detail_path)} is missing and should be true"
                    matches.append(RuleMatch(detail_path, message))
                elif not (value is True or value == "true"):
                    detail_path = path + [key]
                    message = f"Property {'/'.join(detail_path)} should be true"
                    matches.append(RuleMatch(detail_path, message))

        return matches
