# Contains code from https://github.com/awslabs/serverless-rules/tree/0344f9426263be9a08873425511228a0a310116e
# type: ignore
"""
Rules for EventBridge resources
"""

from cfnlint.rules import CloudFormationLintRule, RuleMatch

from .._sam import SAM_DEAD_LETTER_EVENT_TYPES, serverless_function_events


class EventBridgeDLQRule(CloudFormationLintRule):
    """
    Ensure Event Bridge rules have a DLQ configured
    """

    id = "ES4000"  # noqa: VNE003
    shortdesc = "EventBridge DLQ"
    description = "Ensure Event Bridge rules have a DLQ configured"
    source_url = (
        "https://awslabs.github.io/serverless-rules/rules/eventbridge/rule_without_dlq/"
    )
    tags = ["stepfunctions"]

    _message = "EventBridge rule {} should have a DeadLetterConfig.Arn property for all its Targets."
    _sam_message = "Event {} of {} creates an EventBridge rule that should have a DeadLetterConfig.Arn property."  # noqa: E501

    def match(self, cfn):
        """
        Match against EventBridge rules without a DeadLetterConfig for all targets
        """

        matches = []

        for key, value in cfn.get_resources(["AWS::Events::Rule"]).items():
            targets = value.get("Properties", {}).get("Targets", [])

            if not all("Arn" in t.get("DeadLetterConfig", {}) for t in targets):
                matches.append(RuleMatch(["Resources", key], self._message.format(key)))

        for key, value in cfn.get_resources(
            ["AWS::Serverless::Function", "AWS::Serverless::StateMachine"]
        ).items():
            for event_name, event_type, event_properties in serverless_function_events(
                value
            ):
                if event_type not in SAM_DEAD_LETTER_EVENT_TYPES:
                    continue

                if "Arn" not in event_properties.get("DeadLetterConfig", {}):
                    matches.append(
                        RuleMatch(
                            ["Resources", key, "Properties", "Events", event_name],
                            self._sam_message.format(event_name, key),
                        )
                    )

        return matches
