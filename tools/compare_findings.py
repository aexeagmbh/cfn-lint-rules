"""
Print every finding of this package's rules for every fixture, one per line.

Run it once against the last cfn-lint release with the SAM transform and once
against the pinned one, then diff the two outputs to see what the SAM port
changed.

    uv run tools/compare_findings.py > /tmp/after.txt

    uv venv /tmp/venv-1.53.3
    VIRTUAL_ENV=/tmp/venv-1.53.3 uv pip install --no-deps -e .
    VIRTUAL_ENV=/tmp/venv-1.53.3 uv pip install \\
        --exclude-newer 2026-08-11T00:00:00Z 'cfn-lint==1.53.3'
    /tmp/venv-1.53.3/bin/python tools/compare_findings.py > /tmp/before.txt

    diff -u /tmp/before.txt /tmp/after.txt

No PEP 723 header on purpose: the script has to import `cfn_lint_ax` from the
working tree, which an isolated script environment does not provide.
"""

from pathlib import Path

from cfnlint.config import ConfigMixIn
from cfnlint.core import get_rules
from cfnlint.runner import run_template_by_file_path

FIXTURE_DIRS = ("tests/good", "tests/bad", "tests/serverless_rules/templates")


def main() -> None:
    rules = get_rules(
        ["cfn_lint_ax.rules", "cfn_lint_ax.serverless_rules"],
        ignore_rules=[],
        include_rules=["I"],
        include_experimental=True,
    )

    for directory in FIXTURE_DIRS:
        for path in sorted(Path(directory).glob("*.yaml")):
            findings = run_template_by_file_path(
                filename=path.as_posix(),
                config=ConfigMixIn(["--regions", "us-east-1"]),
                rules=rules,
                ignore_bad_template=False,
            )
            for match in sorted(
                findings, key=lambda m: (m.rule.id, "/".join(str(p) for p in m.path))
            ):
                joined = "/".join(str(part) for part in match.path)
                print(f"{path} {match.rule.id} {joined}")


if __name__ == "__main__":
    main()
