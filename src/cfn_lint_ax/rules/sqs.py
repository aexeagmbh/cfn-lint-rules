from typing import List

from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class SqsQueueEncryption(CloudFormationLintRule):  # type: ignore[misc]
    """Rule description"""

    id = "W9311"
    shortdesc = "Configure Queue Encryption"
    description = "Configure SQS Queue encryption with SSE-KMS or SSE-SQS"
    source_url = "https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-data-encryption.html"
    tags = ["sqs", "security"]

    def match(self, cfn: Template) -> List[RuleMatch]:
        matches = []

        resources = cfn.get_resources(["AWS::SQS::Queue"])
        for resource_name, resource in resources.items():
            properties = resource.get("Properties", {})
            sqs_managed_sse_enabled = properties.get("SqsManagedSseEnabled")
            kms_master_key_id = properties.get("KmsMasterKeyId")
            if not (sqs_managed_sse_enabled or kms_master_key_id):
                path = ["Resources", resource_name, "Properties"]
                message = f"Resource {'/'.join(path)} Queue encryption must be enabled by either defining SqsManagedSseEnabled or KmsMasterKeyId."
                matches.append(RuleMatch(path, message))

        return matches
