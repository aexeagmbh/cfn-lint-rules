# Contains code from https://github.com/awslabs/serverless-rules/tree/0344f9426263be9a08873425511228a0a310116e
# type: ignore
"""
Testing utility functions
"""


import pytest

from cfn_lint_ax import _utils as utils

value_test_cases = [
    # str
    pytest.param({"input": "MyString", "id": "MyString", "references": []}, id="str"),
    # Ref
    pytest.param(
        {
            "input": {"Ref": "MyResource"},
            "id": "MyResource",
            "references": ["MyResource"],
        },
        id="Ref",
    ),
    # Fn::GetAtt
    pytest.param(
        {
            "input": {"Fn::GetAtt": ["MyResource", "Arn"]},
            "id": "MyResource.Arn",
            "references": ["MyResource"],
        },
        id="Fn::GetAtt",
    ),
    # Fn::Join
    pytest.param(
        {
            "input": {"Fn::Join": ["/", ["ABC", "DEF"]]},
            "id": "ABC/DEF",
            "references": [],
        },
        id="Fn::Join",
    ),
    # Fn::Join with references
    pytest.param(
        {
            "input": {"Fn::Join": ["/", ["ABC", {"Ref": "MyResource"}]]},
            "id": "ABC/MyResource",
            "references": ["MyResource"],
        },
        id="Fn::Join_with_references",
    ),
    # Fn::Sub
    pytest.param(
        {
            "input": {"Fn::Sub": "abc-${MyResource}"},
            "id": "abc-${MyResource}",
            "references": ["MyResource"],
        },
        id="Fn::Sub",
    ),
    # Fn::Sub with hard-coded variables
    pytest.param(
        {
            "input": {"Fn::Sub": ["abc-${MyVar}", {"MyVar": "MyResource"}]},
            "id": "abc-MyResource",
            "references": [],
        },
        id="Fn::Sub_with_hard_coded_variables",
    ),
    # Fn::Sub with variables and references
    pytest.param(
        {
            "input": {"Fn::Sub": ["abc-${MyVar}", {"MyVar": {"Ref": "MyResource"}}]},
            "id": "abc-${MyVar}",
            "references": ["MyResource"],
        },
        id="Fn::Sub_with_variables_and_references",
    ),
]


@pytest.mark.parametrize("case", value_test_cases)
def test_value(case):
    """
    Test Value()
    """

    print(f"case: {case}")

    output = utils.Value(case["input"])

    print(f"output id: {output.id}")
    print(f"output ref: {output.references}")

    assert case["id"] == output.id
    assert case["references"] == output.references


def test_none_value():
    """
    Test Value(None)
    """

    output = utils.Value(None)
    assert output is None
