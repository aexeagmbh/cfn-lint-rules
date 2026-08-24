from cfnlint.schema import PROVIDER_SCHEMA_MANAGER

from cfn_lint_ax._sam import (
    SAM_ASYNC_EVENT_PRINCIPALS,
    SAM_DEAD_LETTER_EVENT_TYPES,
    SAM_EVENT_BRIDGE_EVENT_TYPES,
    SAM_EVENT_PRINCIPALS,
    SAM_EVENT_SOURCE_MAPPING_DESTINATION_EVENT_TYPES,
    SAM_EVENT_SOURCE_MAPPING_EVENT_TYPES,
    SAM_GENERATED_RESOURCE_TYPES,
    serverless_function_events,
)


def _event_properties(event_type: str) -> set[str]:
    """
    Property names the SAM schema allows for an event of `event_type`
    """

    schema = PROVIDER_SCHEMA_MANAGER.get_resource_schema(
        "us-east-1", "AWS::Serverless::Function"
    ).schema
    definitions = schema["definitions"]
    # `CloudWatchEvent` is already named after its type, the others are not
    name = f"{event_type}Event"
    event = definitions[name if name in definitions else event_type]
    reference = event["properties"]["Properties"]["allOf"][0]["$ref"]
    return set(definitions[reference.rsplit("/", 1)[-1]]["properties"])


def test_mapping_covers_exactly_the_sam_types_cfn_lint_knows() -> None:
    known = {
        resource_type
        for resource_type in PROVIDER_SCHEMA_MANAGER.get_resource_types("us-east-1")
        if resource_type.startswith("AWS::Serverless::")
    }
    assert set(SAM_GENERATED_RESOURCE_TYPES) == known


def test_every_generated_type_is_a_real_resource_type() -> None:
    known = set(PROVIDER_SCHEMA_MANAGER.get_resource_types("us-east-1"))
    generated = {
        resource_type
        for types in SAM_GENERATED_RESOURCE_TYPES.values()
        for resource_type in types
    }
    assert generated <= known


def test_a_function_generates_its_on_failure_destinations() -> None:
    generated = SAM_GENERATED_RESOURCE_TYPES["AWS::Serverless::Function"]
    assert "AWS::SQS::Queue" in generated
    assert "AWS::SNS::Topic" in generated


def test_events_are_yielded_with_their_type_and_properties() -> None:
    resource = {
        "Type": "AWS::Serverless::Function",
        "Properties": {
            "Events": {
                "Sns": {
                    "Type": "SNS",
                    "Properties": {"Topic": "arn:aws:sns:us-east-1:1:t"},
                },
            }
        },
    }
    assert list(serverless_function_events(resource)) == [
        ("Sns", "SNS", {"Topic": "arn:aws:sns:us-east-1:1:t"})
    ]


def test_malformed_events_are_skipped() -> None:
    resource = {
        "Type": "AWS::Serverless::Function",
        "Properties": {
            "Events": {
                "NotADict": "oops",
                "NoType": {"Properties": {}},
                "NoProperties": {"Type": "SNS"},
            }
        },
    }
    assert list(serverless_function_events(resource)) == [("NoProperties", "SNS", {})]


def test_a_resource_without_events_yields_nothing() -> None:
    assert not list(serverless_function_events({"Type": "AWS::Serverless::Function"}))


def test_event_principals_match_the_sam_transform() -> None:
    assert SAM_EVENT_PRINCIPALS == {
        "AlexaSkill": "alexa-appkit.amazon.com",
        "Api": "apigateway.amazonaws.com",
        "CloudWatchEvent": "events.amazonaws.com",
        "CloudWatchLogs": "logs.amazonaws.com",
        "Cognito": "cognito-idp.amazonaws.com",
        "EventBridgeRule": "events.amazonaws.com",
        "HttpApi": "apigateway.amazonaws.com",
        "IoTRule": "iot.amazonaws.com",
        "S3": "s3.amazonaws.com",
        "SNS": "sns.amazonaws.com",
        "Schedule": "events.amazonaws.com",
    }


def test_async_principals_are_a_subset_of_the_event_principals() -> None:
    assert SAM_ASYNC_EVENT_PRINCIPALS <= set(SAM_EVENT_PRINCIPALS.values())


def test_event_source_mapping_event_types() -> None:
    assert SAM_EVENT_SOURCE_MAPPING_EVENT_TYPES == frozenset(
        {
            "DocumentDB",
            "DynamoDB",
            "Kinesis",
            "MSK",
            "SQS",
            "SelfManagedKafka",
        }
    )


def test_event_bridge_event_types() -> None:
    assert SAM_EVENT_BRIDGE_EVENT_TYPES == frozenset(
        {"CloudWatchEvent", "EventBridgeRule", "Schedule"}
    )


def test_only_event_types_with_a_destination_ask_for_one() -> None:
    for event_type in SAM_EVENT_SOURCE_MAPPING_EVENT_TYPES:
        has_destination = "DestinationConfig" in _event_properties(event_type)
        assert has_destination == (
            event_type in SAM_EVENT_SOURCE_MAPPING_DESTINATION_EVENT_TYPES
        ), event_type


def test_only_event_types_with_a_dead_letter_config_ask_for_one() -> None:
    for event_type in SAM_EVENT_BRIDGE_EVENT_TYPES:
        has_dead_letter_config = "DeadLetterConfig" in _event_properties(event_type)
        assert has_dead_letter_config == (
            event_type in SAM_DEAD_LETTER_EVENT_TYPES
        ), event_type


def test_a_sam_sns_event_still_cannot_carry_a_redrive_policy() -> None:
    # ES7000 reports every SNS event, because the `RedrivePolicy` that fixes it
    # is missing from SAM's own schema source and therefore from the schema
    # cfn-lint generates out of it - see `serverless_rules/sns.py`. When this
    # test starts failing, SAM fixed its schema and cfn-lint imported it, so
    # the note there and the missing `es7000-sam.pass.yaml` can be revisited.
    assert "RedrivePolicy" not in _event_properties("SNS")
