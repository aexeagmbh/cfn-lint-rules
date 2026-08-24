# Contains code from https://github.com/awslabs/serverless-rules/tree/0344f9426263be9a08873425511228a0a310116e
# type: ignore
"""
Rules for SNS resources
"""

from cfnlint.rules import CloudFormationLintRule, RuleMatch

from .._sam import serverless_function_events


class SnsNoRedrivePolicyRule(CloudFormationLintRule):
    """
    Ensure SNS subscriptions have a redrive policy configured
    """

    id = "ES7000"  # noqa: VNE003
    shortdesc = "SNS No Redrive Policy"
    description = "Ensure SNS subscriptions have a redrive policy configured"
    source_url = "https://awslabs.github.io/serverless-rules/rules/sns/redrive_policy/"
    tags = ["sns"]

    _message = "SNS Subscription {} should have a RedrivePolicy property configured."
    _sam_message = "Event {} of {} creates an SNS subscription that should have a RedrivePolicy property configured."  # noqa: E501

    def match(self, cfn):
        """
        Match against SNS subscriptions without RedrivePolicy
        """

        matches = []

        for key, value in cfn.get_resources(["AWS::SNS::Subscription"]).items():
            redrive_policy = value.get("Properties", {}).get("RedrivePolicy", None)

            if redrive_policy is None:
                matches.append(RuleMatch(["Resources", key], self._message.format(key)))

        # `aws-sam-translator` copies a `RedrivePolicy` from an `SNS` event onto
        # the subscription it generates, but its schema source omits the
        # property - `model/eventsources/push.py` declares it,
        # `internal/schema_source/aws_serverless_function.py` does not. cfn-lint
        # generates its SAM schemas from the latter, so it answers a template
        # that sets it with `E3002`, and the only finding-free fix is an
        # explicit `AWS::SNS::Subscription`. Fixing it means fixing SAM's schema
        # source; cfn-lint picks that up on its next schema import.
        # `tests/test_sam.py` fails once it has, and an `es7000-sam.pass.yaml`
        # fixture becomes possible.
        for key, value in cfn.get_resources(["AWS::Serverless::Function"]).items():
            for event_name, event_type, event_properties in serverless_function_events(
                value
            ):
                if event_type != "SNS":
                    continue

                if event_properties.get("RedrivePolicy") is None:
                    matches.append(
                        RuleMatch(
                            ["Resources", key, "Properties", "Events", event_name],
                            self._sam_message.format(event_name, key),
                        )
                    )

        return matches
