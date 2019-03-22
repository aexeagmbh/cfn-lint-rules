from cfnlint import CloudFormationLintRule, RuleMatch


class S3BucketEncryption(CloudFormationLintRule):
    """Rule description """

    id = "W9302"
    shortdesc = "Configure S3 Server-Side Encryption"
    description = "Configure S3 Server-Side Encryption with AES256 or aws:kms."
    source_url = (
        "https://docs.aws.amazon.com/AmazonS3/latest/dev/serv-side-encryption.html"
    )
    tags = ["s3", "security"]

    def match(self, cfn):
        matches = []

        resources = cfn.get_resources(["AWS::S3::Bucket"])
        for resource_name, resource in resources.items():
            properties = resource.get("Properties", {})
            if not "BucketEncryption" in properties:
                path = ["Resources", resource_name, "Properties", "BucketEncryption"]
                message = f"Property {'/'.join(path)} is missing"
                matches.append(RuleMatch(path, message))

        return matches
