# /// script
# requires-python = ">=3.12"
# dependencies = ["aws-sam-translator==1.111.0", "boto3"]
# ///
"""
Collect the CloudFormation resource types the SAM transform generates.

cfn-lint >= 1.54.0 no longer applies the SAM transform, so rules see the
`AWS::Serverless::*` resources of a template instead of the resources
CloudFormation deploys them as. `src/cfn_lint_ax/_sam.py` needs to know that
mapping; this script produces it by transforming minimal templates with the
real `aws-sam-translator`.

Run with:

    AWS_DEFAULT_REGION=us-east-1 uv run tools/collect_sam_resource_types.py

It makes no AWS calls: the managed policy loader is stubbed out and the region
is only used to build ARNs.
"""

from typing import Any

from samtranslator.translator.transform import transform  # pylint: disable=import-error

FUNCTION_PROPERTIES: dict[str, Any] = {
    "CodeUri": "s3://bucket/key",
    "Runtime": "python3.12",
    "Handler": "main.handler",
}

# Every property that makes SAM generate an extra resource, so that the
# collected set is the union over all shapes of a resource.
TEMPLATES: dict[str, dict[str, Any]] = {
    "AWS::Serverless::Function": {
        "Resource": {
            "Type": "AWS::Serverless::Function",
            "Properties": {
                **FUNCTION_PROPERTIES,
                "AutoPublishAlias": "live",
                "DeploymentPreference": {"Type": "AllAtOnce"},
                "FunctionUrlConfig": {"AuthType": "NONE"},
                "EventInvokeConfig": {
                    "DestinationConfig": {"OnFailure": {"Type": "SQS"}}
                },
                "Events": {
                    "Schedule": {
                        "Type": "Schedule",
                        "Properties": {"Schedule": "rate(5 minutes)"},
                    },
                    "ScheduleV2": {
                        "Type": "ScheduleV2",
                        "Properties": {"ScheduleExpression": "rate(5 minutes)"},
                    },
                    "Sns": {
                        "Type": "SNS",
                        "Properties": {
                            "Topic": "arn:aws:sns:us-east-1:111122223333:topic"
                        },
                    },
                    "IoTRule": {
                        "Type": "IoTRule",
                        "Properties": {"Sql": "SELECT * FROM 'topic'"},
                    },
                    "Sqs": {
                        "Type": "SQS",
                        "Properties": {
                            "Queue": "arn:aws:sqs:us-east-1:111122223333:queue",
                            "BatchSize": 1,
                        },
                    },
                    "CloudWatchLogs": {
                        "Type": "CloudWatchLogs",
                        "Properties": {
                            "LogGroupName": "log-group",
                            "FilterPattern": "",
                        },
                    },
                },
            },
        },
    },
    "AWS::Serverless::Function/OnFailureSns": {
        "Resource": {
            "Type": "AWS::Serverless::Function",
            "Properties": {
                **FUNCTION_PROPERTIES,
                "EventInvokeConfig": {
                    "DestinationConfig": {"OnFailure": {"Type": "SNS"}}
                },
            },
        },
    },
    "AWS::Serverless::Api": {
        "Resource": {
            "Type": "AWS::Serverless::Api",
            "Properties": {
                "StageName": "prod",
                "DefinitionBody": {
                    "openapi": "3.0.1",
                    "info": {"title": "test-api", "version": "1.0.0"},
                    "paths": {
                        "/": {
                            "get": {
                                "responses": {},
                                "x-amazon-apigateway-integration": {"type": "mock"},
                            }
                        }
                    },
                },
                "ApiKeySourceType": "HEADER",
                "Auth": {
                    "ApiKeyRequired": True,
                    "UsagePlan": {"CreateUsagePlan": "PER_API"},
                },
                "Domain": {
                    "DomainName": "example.com",
                    "CertificateArn": (
                        "arn:aws:acm:us-east-1:111122223333:certificate/abc"
                    ),
                    "Route53": {"HostedZoneId": "Z1"},
                },
            },
        },
    },
    "AWS::Serverless::HttpApi": {
        "Resource": {
            "Type": "AWS::Serverless::HttpApi",
            "Properties": {
                "StageName": "prod",
                "DefinitionUri": "s3://bucket/key",
                "Domain": {
                    "DomainName": "example.com",
                    "CertificateArn": (
                        "arn:aws:acm:us-east-1:111122223333:certificate/abc"
                    ),
                    "Route53": {"HostedZoneId": "Z1"},
                },
            },
        },
    },
    "AWS::Serverless::StateMachine": {
        "Resource": {
            "Type": "AWS::Serverless::StateMachine",
            "Properties": {
                "Definition": {"StartAt": "S", "States": {"S": {"Type": "Succeed"}}},
                "Events": {
                    "Schedule": {
                        "Type": "Schedule",
                        "Properties": {"Schedule": "rate(5 minutes)"},
                    },
                    "ScheduleV2": {
                        "Type": "ScheduleV2",
                        "Properties": {"ScheduleExpression": "rate(5 minutes)"},
                    },
                },
            },
        },
    },
    "AWS::Serverless::SimpleTable": {
        "Resource": {"Type": "AWS::Serverless::SimpleTable"},
    },
    "AWS::Serverless::LayerVersion": {
        "Resource": {
            "Type": "AWS::Serverless::LayerVersion",
            "Properties": {"ContentUri": "s3://bucket/key"},
        },
    },
    "AWS::Serverless::Application": {
        "Resource": {
            "Type": "AWS::Serverless::Application",
            "Properties": {"Location": "https://example.com/template.yaml"},
        },
    },
    "AWS::Serverless::GraphQLApi": {
        "Resource": {
            "Type": "AWS::Serverless::GraphQLApi",
            "Properties": {
                "SchemaInline": "type Query { a: String }",
                "Auth": {"Type": "AWS_IAM"},
                "ApiKeys": {"Key": {}},
                "Cache": {
                    "ApiCachingBehavior": "FULL_REQUEST_CACHING",
                    "Ttl": 1,
                    "Type": "SMALL",
                },
                "DataSources": {
                    "Lambda": {
                        "Source": {
                            "FunctionArn": (
                                "arn:aws:lambda:us-east-1:111122223333:function:f"
                            )
                        }
                    }
                },
                "Functions": {
                    "Fn": {
                        "DataSource": "Source",
                        "Runtime": {"Name": "APPSYNC_JS", "Version": "1.0.0"},
                        "InlineCode": "x",
                    }
                },
                "Resolvers": {
                    "Query": {
                        "a": {
                            "Runtime": {"Name": "APPSYNC_JS", "Version": "1.0.0"},
                            "InlineCode": "x",
                            "Pipeline": ["Fn"],
                        }
                    }
                },
            },
        },
    },
    "AWS::Serverless::Connector/ToQueue": {
        "Source": {
            "Type": "AWS::Serverless::Function",
            "Properties": FUNCTION_PROPERTIES,
        },
        "Destination": {"Type": "AWS::SQS::Queue"},
        "Resource": {
            "Type": "AWS::Serverless::Connector",
            "Properties": {
                "Source": {"Id": "Source"},
                "Destination": {"Id": "Destination"},
                "Permissions": ["Write"],
            },
        },
    },
    "AWS::Serverless::Connector/ToFunction": {
        "Source": {"Type": "AWS::SNS::Topic"},
        "Destination": {
            "Type": "AWS::Serverless::Function",
            "Properties": FUNCTION_PROPERTIES,
        },
        "Resource": {
            "Type": "AWS::Serverless::Connector",
            "Properties": {
                "Source": {"Id": "Source"},
                "Destination": {"Id": "Destination"},
                "Permissions": ["Write"],
            },
        },
    },
}


class _StubManagedPolicyLoader:
    """Stands in for the loader that would call IAM."""

    def load(self) -> dict[str, str]:
        return {}

    def get_policy_map(self) -> dict[str, str]:
        return {}


def _transform_types(resources: dict[str, Any]) -> set[str]:
    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Transform": "AWS::Serverless-2016-10-31",
        "Resources": resources,
    }
    output = transform(template, {}, _StubManagedPolicyLoader())
    return {resource["Type"] for resource in output["Resources"].values()}


def _generated_types(resources: dict[str, Any]) -> set[str]:
    """
    Types the `Resource` entry generates.

    A template may carry helper resources so that the resource under test has
    something to point at - a connector needs a source and a destination. What
    those generate on their own belongs to their own entry, so transform them
    without the resource under test and subtract the result.
    """

    helpers = {key: value for key, value in resources.items() if key != "Resource"}
    baseline = _transform_types(helpers) if helpers else set()
    return _transform_types(resources) - baseline


def main() -> None:
    collected: dict[str, set[str]] = {}
    for name, resources in TEMPLATES.items():
        sam_type = name.split("/", maxsplit=1)[0]
        collected.setdefault(sam_type, set()).update(_generated_types(resources))

    print("SAM_GENERATED_RESOURCE_TYPES: dict[str, frozenset[str]] = {")
    for sam_type, types in sorted(collected.items()):
        print(f"    {sam_type!r}: frozenset(")
        print("        {")
        for generated in sorted(types):
            print(f"            {generated!r},")
        print("        }")
        print("    ),")
    print("}")


if __name__ == "__main__":
    main()
