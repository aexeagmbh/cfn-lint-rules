from tests.utils import BAD_TEMPLATE_FIXTURES_PATH, assert_all_matches

from rules.s3_bucket_encryption import S3BucketEncryption


def test_bad_s3_bucket_encryption():
    filename = BAD_TEMPLATE_FIXTURES_PATH / "s3_bucket_without_bucket_encryption.yaml"
    expected_errors = [
        (
            5,
            S3BucketEncryption,
            "Property Resources/TestBucket/Properties/BucketEncryption is missing",
        )
    ]

    assert_all_matches(filename, expected_errors)
