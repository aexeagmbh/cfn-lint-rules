from tests.utils import BAD_TEMPLATE_FIXTURES_PATH, assert_all_matches

from rules.metadata_ax_changeset_auto_approve import MetadataAxChangesetAutoApprove


def test_bad_metadata_ax_changeset_auto_approve():
    filename = (
        BAD_TEMPLATE_FIXTURES_PATH / "metadata_ax_changeset_auto_approve.yaml"
    ).as_posix()
    expected_errors = [
        (
            4,
            MetadataAxChangesetAutoApprove,
            "Metadata/AxChangesetAutoApprove/Add must be a list of strings.",
        ),
        (
            6,
            MetadataAxChangesetAutoApprove,
            "Metadata/AxChangesetAutoApprove/ModifyConditionalReplacement[0] Bucket is not a resource type used in this template",
        ),
        (
            8,
            MetadataAxChangesetAutoApprove,
            "Metadata/AxChangesetAutoApprove/ModifyReplacement must be a list of strings.",
        ),
        (
            10,
            MetadataAxChangesetAutoApprove,
            "Metadata/AxChangesetAutoApprove/Remove[0] must be a string.",
        ),
        (
            11,
            MetadataAxChangesetAutoApprove,
            "Metadata/AxChangesetAutoApprove/BadKey key BadKey is not allowed. Allowed keys for AxChangesetAutoApprove: Add, ModifyConditionalReplacement, ModifyReplacement, Remove.",
        ),
    ]

    assert_all_matches(filename, expected_errors)
