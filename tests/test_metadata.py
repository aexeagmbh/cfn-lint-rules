from typing import Any

from cfnlint.template import Template

from cfn_lint_ax.rules import MetadataAxChangesetAutoApprove

SERVERLESS_TEMPLATE: dict[str, Any] = {
    "Transform": "AWS::Serverless-2016-10-31",
    "Metadata": {
        "AxChangesetAutoApprove": {
            "Add": [
                "AWS::Lambda::Function",
                "AWS::Lambda::Permission",
            ]
        }
    },
    "Resources": {
        "MyFunction": {
            "Type": "AWS::Serverless::Function",
            "Properties": {
                "Handler": "index.handler",
                "Runtime": "python3.13",
                "CodeUri": ".",
            },
        },
    },
}


def get_matches(template: dict[str, Any]) -> list[str]:
    cfn = Template("test.yaml", template, regions=["us-east-1"])
    rule = MetadataAxChangesetAutoApprove()
    rule.initialize(cfn)
    return [match.message for match in rule.match(cfn)]


def test_types_generated_by_a_serverless_function_are_allowed() -> None:
    # cfn-lint >= 1.54 no longer applies the SAM transform, so the rule only
    # sees `AWS::Serverless::Function` and has to know which resource types it
    # generates.
    assert not get_matches(SERVERLESS_TEMPLATE)


def test_types_not_generated_by_a_serverless_function_are_reported() -> None:
    template = {
        **SERVERLESS_TEMPLATE,
        "Metadata": {"AxChangesetAutoApprove": {"Add": ["AWS::S3::Bucket"]}},
    }
    assert get_matches(template) == [
        "Metadata/AxChangesetAutoApprove/Add[0] AWS::S3::Bucket is not a resource"
        " type used in this template"
    ]


def test_types_generated_by_an_implicit_api_are_allowed() -> None:
    template = {
        **SERVERLESS_TEMPLATE,
        "Metadata": {
            "AxChangesetAutoApprove": {"Add": ["AWS::ApiGateway::Stage"]},
        },
        "Resources": {
            "MyFunction": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Handler": "index.handler",
                    "Runtime": "python3.13",
                    "CodeUri": ".",
                    "Events": {
                        "MyApi": {
                            "Type": "Api",
                            "Properties": {"Path": "/foo", "Method": "get"},
                        },
                    },
                },
            },
        },
    }
    assert not get_matches(template)


def test_unknown_serverless_resource_types_disable_the_check() -> None:
    # Without knowing which resources SAM generates for a resource type, every
    # type in the list could be a valid one.
    template = {
        **SERVERLESS_TEMPLATE,
        "Resources": {
            "MyThing": {"Type": "AWS::Serverless::SomethingNew", "Properties": {}},
        },
    }
    assert not get_matches(template)


def test_types_generated_by_an_on_failure_queue_are_allowed() -> None:
    # `EventInvokeConfig.DestinationConfig.OnFailure.Type: SQS` makes SAM
    # generate the queue, so `AWS::SQS::Queue` is a type this template uses.
    template = {
        **SERVERLESS_TEMPLATE,
        "Metadata": {"AxChangesetAutoApprove": {"Add": ["AWS::SQS::Queue"]}},
        "Resources": {
            "MyFunction": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Handler": "index.handler",
                    "Runtime": "python3.13",
                    "CodeUri": ".",
                    "EventInvokeConfig": {
                        "DestinationConfig": {"OnFailure": {"Type": "SQS"}}
                    },
                },
            },
        },
    }
    assert not get_matches(template)
