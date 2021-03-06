from rules.s3_bucket_encryption import S3BucketEncryption
from tests.utils import BAD_TEMPLATE_FIXTURES_PATH, assert_all_matches


def test_bad_s3_bucket_encryption() -> None:
    filename = (
        BAD_TEMPLATE_FIXTURES_PATH / "s3_bucket_without_bucket_encryption.yaml"
    ).as_posix()
    expected_errors = [
        (
            5,
            S3BucketEncryption,
            "Property Resources/TestBucket/Properties/BucketEncryption is missing",
        )
    ]

    assert_all_matches(filename, expected_errors)
