from cfnlint.rules import CloudFormationLintRule, RuleMatch


class UnresolvedObject(CloudFormationLintRule):
    """Rule description """

    id = "E9402"
    shortdesc = "Resolve objects"
    description = "Validate that Fn::Sub does not contain unresolved objects"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html"
    tags = ["sub"]

    def match(self, cfn):
        matches = []

        sub_objs = cfn.search_deep_keys("Fn::Sub")

        for sub_obj in sub_objs:
            sub_value_obj = sub_obj[-1]
            if "object at" in sub_value_obj:
                message = "Sub contains an unresolved object"
                matches.append(RuleMatch(sub_obj, message))

        return matches
