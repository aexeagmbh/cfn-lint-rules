from tests.utils import GOOD_TEMPLATE_FIXTURES_PATH, get_cnflint_errors


def test_good(good_template: str) -> None:
    filename = (GOOD_TEMPLATE_FIXTURES_PATH / good_template).as_posix()
    errors = get_cnflint_errors(template_path=filename)
    assert not errors, errors
