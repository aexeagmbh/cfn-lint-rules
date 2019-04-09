from cfnlint import CloudFormationLintRule, RuleMatch


class MetadataAxChangesetAutoApprove(CloudFormationLintRule):
    id = "E9401"
    shortdesc = "Validate Metadata AxChangesetAutoApprove schema"
    description = "Validate Metadata AxChangesetAutoApprove schema"
    # source_url = ""
    tags = ["metadata"]
    experimental = True

    allowed_template_ax_changeset_auto_approve_keys = {
        "Add",
        "ModifyConditionalReplacement",
        "ModifyReplacement",
        "Remove",
    }
    base_path = ["Metadata", "AxChangesetAutoApprove"]

    def initialize(self, cfn):
        self.used_cloudformation_resource_types = {
            resource.get("Type") for resource in cfn.get_resources().values()
        }

    def match(self, cfn):
        matches = []

        template_metadata = cfn.template.get("Metadata", {})

        if "AxChangesetAutoApprove" in template_metadata:
            template_ax_changeset_auto_approve = template_metadata[
                "AxChangesetAutoApprove"
            ]
            matches.extend(
                self.check_template_ax_changeset_auto_approve(
                    template_ax_changeset_auto_approve
                )
            )

        return matches

    def check_template_ax_changeset_auto_approve(
        self, template_ax_changeset_auto_approve
    ):
        if not isinstance(template_ax_changeset_auto_approve, dict):
            yield RuleMatch(
                self.base_path, "Metadata/AxChangesetAutoApprove must be a mapping."
            )
            return  # stop any further checks, we need template_ax_changeset_auto_approve to be a dict for them

        excess_keys = (
            template_ax_changeset_auto_approve.keys()
            - self.allowed_template_ax_changeset_auto_approve_keys
        )
        for excess_key in excess_keys:
            path = self.base_path + [excess_key]
            path_str = "/".join(path)
            allowed_keys = ", ".join(
                sorted(self.allowed_template_ax_changeset_auto_approve_keys)
            )
            yield RuleMatch(
                path,
                f"{path_str} key {excess_key} is not allowed. Allowed keys for AxChangesetAutoApprove: {allowed_keys}.",
            )

        available_items = {
            k: v
            for k, v in template_ax_changeset_auto_approve.items()
            if k in self.allowed_template_ax_changeset_auto_approve_keys
        }

        for key, value in available_items.items():
            # yield from self.check_template_ax_changeset_auto_approve_key(key, value)
            key_path = self.base_path + [key]
            if not isinstance(value, list):
                path_str = "/".join(key_path)
                yield RuleMatch(key_path, f"{path_str} must be a list of strings.")
                continue

            for list_idx, element in enumerate(value):
                path = key_path + [list_idx]
                path_str = "/".join(key_path) + f"[{list_idx}]"
                if not isinstance(element, str):
                    yield RuleMatch(path, f"{path_str} must be a string.")
                else:
                    if element not in self.used_cloudformation_resource_types:
                        yield RuleMatch(
                            path,
                            f"{path_str} {element} is not a resource type used in this template",
                        )
