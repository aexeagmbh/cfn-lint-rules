from typing import List

import pytest

from cfn_lint_ax.rules import S3BucketPublicAccess
from tests.utils import BAD_TEMPLATE_FIXTURES_PATH, ExpectedError, assert_all_matches


@pytest.mark.parametrize(
    "filename,expected_errors",
    [
        (
            "s3_bucket_with_bad_public_access_block_configuration.yaml",
            [
                (
                    10,
                    S3BucketPublicAccess,
                    "Property Resources/TestBucket1/Properties/PublicAccessBlockConfiguration/BlockPublicPolicy is missing and should be true",
                ),
                (
                    10,
                    S3BucketPublicAccess,
                    "Property Resources/TestBucket1/Properties/PublicAccessBlockConfiguration/IgnorePublicAcls is missing and should be true",
                ),
                (
                    11,
                    S3BucketPublicAccess,
                    "Property Resources/TestBucket1/Properties/PublicAccessBlockConfiguration/BlockPublicAcls should be true",
                ),
                (
                    23,
                    S3BucketPublicAccess,
                    "Property Resources/TestBucket2/Properties/PublicAccessBlockConfiguration/RestrictPublicBuckets is missing and should be true",
                ),
                (
                    26,
                    S3BucketPublicAccess,
                    "Property Resources/TestBucket2/Properties/PublicAccessBlockConfiguration/IgnorePublicAcls should be true",
                ),
            ],
        ),
        (
            "s3_bucket_without_public_access_block_configuration.yaml",
            [
                (
                    5,
                    S3BucketPublicAccess,
                    "Property Resources/TestBucket/Properties/PublicAccessBlockConfiguration is missing",
                )
            ],
        ),
    ],
)
def test_bad_s3_bucket_encryption(
    filename: str, expected_errors: List[ExpectedError]
) -> None:
    filename = (BAD_TEMPLATE_FIXTURES_PATH / filename).as_posix()

    assert_all_matches(filename, expected_errors)
