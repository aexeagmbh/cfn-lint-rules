from typing import List

import pytest

from cfn_lint_ax.rules import CertificateManagerCertificateNameTag
from tests.utils import BAD_TEMPLATE_FIXTURES_PATH, ExpectedError, assert_all_matches


@pytest.mark.parametrize(
    "filename,expected_errors",
    [
        (
            "certificate_manager_certificate_without_name.yaml",
            [
                (
                    5,
                    CertificateManagerCertificateNameTag,
                    "Property Resources/Certificate1/Properties/Tags is missing 'Name' tag",
                ),
                (
                    11,
                    CertificateManagerCertificateNameTag,
                    "Property Resources/Certificate2/Properties/Tags is missing 'Name' tag",
                ),
            ],
        ),
    ],
)
def test_bad_cloudfront_distribution_config(
    filename: str, expected_errors: List[ExpectedError]
) -> None:
    filename = (BAD_TEMPLATE_FIXTURES_PATH / filename).as_posix()

    assert_all_matches(filename, expected_errors)
