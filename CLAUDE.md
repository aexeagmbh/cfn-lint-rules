# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`cfn-lint-ax` on PyPI: additional [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) rules used at AX Semantics. Requires cfn-lint >= 1.54.0, the release that dropped the SAM transform (see `_sam.py` below). Supports Python 3.10–3.14 and mypy targets 3.10, so avoid newer syntax and stdlib APIs.

## Commands

The project is uv-managed: run tools through `uv run`, install with `uv sync --frozen`. Run tests from the repo root, because fixture paths are resolved relative to the working directory.

- Everything CI checks: `./run_tests.sh`. It *rewrites* files with black and isort, while CI only checks (`black --check`, `isort --check-only --diff`).
- Tests: `uv run pytest`
- One AX rule: `uv run pytest tests/test_bad_templates.py -k W9311`
- One serverless rule: `uv run pytest tests/serverless_rules/test_templates.py -k es7000`
- Linters: `uv run flake8 .`, `uv run pylint --recursive=y ./`, `uv run mypy .`, `uv run yamllint --strict <files>`
- Run the rules on a template: `uv run cfn-lint template.yaml -a cfn_lint_ax.rules`. Add `-a cfn_lint_ax.serverless_rules` for the serverless rules.

## Architecture

There are two independent rule packages under `src/cfn_lint_ax/`, each loaded by module path. cfn-lint finds rules by scanning the package namespace. **A new rule class must therefore be imported and listed in `__all__` in its package's `__init__.py`.** Otherwise cfn-lint ignores it without any error.

- `rules/`: AX's own rules.
  - IDs match `[IWE]9xxx`, enforced by `tests/test_rule_ids.py`. The second digit follows cfn-lint's grouping (README: 1 functions, 3 resources, 4 metadata, …).
  - Fully typed (mypy `disallow_untyped_defs`). Classes carry `# type: ignore[misc]` because `CloudFormationLintRule` is untyped.
  - Each rule is listed in README's rule list, so update the list when you add a rule.
- `serverless_rules/`: vendored from awslabs/serverless-rules, as the header comment says.
  - IDs are `ES` or `WS` plus 4 digits. Tests tell these rules apart by the second character `S`.
  - Files opt out of mypy with a `# type: ignore` header, and `id` lines carry `# noqa: VNE003`.
- `_utils.Value` resolves a CloudFormation value (`Ref`, `GetAtt`, `Join`, `Sub`) to an id string and the logical ids it references. The serverless rules use it to follow references.
- `_sam.py` holds what the package knows about SAM. Since cfn-lint 1.54, rules see `AWS::Serverless::*` resources as written, not the resources CloudFormation deploys them as.
  - A rule that checks a type SAM generates must also check the SAM resource. The established pattern:
    - A second loop over `AWS::Serverless::Function`, using `serverless_function_events()`.
    - It reports at `Resources/<fn>/Properties/Events/<event>` with a separate `_sam_message`.
  - Only report what a SAM property can actually fix, and drop the check otherwise. `docs/sam-transform-removal.md` gives the reasoning for each rule.
  - `tools/collect_sam_resource_types.py` generates `SAM_GENERATED_RESOURCE_TYPES` and `SAM_EVENT_PRINCIPALS`. Regenerate them instead of editing them by hand: `AWS_DEFAULT_REGION=us-east-1 uv run tools/collect_sam_resource_types.py`.
  - `tests/test_sam.py` checks these tables against the SAM schema bundled with cfn-lint, so a cfn-lint upgrade that changes SAM fails a test.
  - `test_a_sam_sns_event_still_cannot_carry_a_redrive_policy` is expected to fail once upstream SAM fixes its schema. When that happens, revisit ES7000 (`serverless_rules/sns.py`).
  - `tools/compare_findings.py` prints every finding for every fixture, so you can diff behaviour between cfn-lint versions. Its docstring explains how.

## Tests and fixtures

Fixtures are also linted by cfn-lint's **built-in rules**, including informational (`I`) and experimental rules. Any finding the test does not expect makes it fail. A fixture must therefore produce no findings except from the rule it targets.

- `rules/` fixtures live in `tests/bad` and `tests/good`:
  - Every rule needs at least one `tests/bad/<RULEID>_<description>.yaml`.
  - Every bad fixture needs an entry in `test_parameters` in `tests/test_bad_templates.py`. The entry lists the exact `(line, message)` pair of every expected finding.
  - `tests/good/*.yaml` must produce no findings.
  - Taggable resources need the I9303 cost allocation tags: `Project`, `ProjectPart: !Ref AWS::StackName` and `ProjectPartDetail: <logical id>`.
  - Stateful resources need `DeletionPolicy` and `UpdateReplacePolicy`, which cfn-lint checks in I3011.
- `serverless_rules/` fixtures live in `tests/serverless_rules/templates`:
  - Name them `<ruleid>[-variant].pass.yaml` or `<ruleid>[-variant].fail.yaml`. The test reads the rule ID from the filename.
  - Every ES or WS rule needs at least one fixture.
  - Only the serverless rules and the built-in rules run here, in region `eu-west-1`, so no cost allocation tags are needed.
- YAML style: yamllint in strict mode, 2-space indent, indented sequences, lines of at most 135 characters.

## Conventions

- Commit subjects follow `[area] Imperative summary`, e.g. `[serverless_rules] …`, `[tags] …`, `[ci] …`, `[deps] …`.
- To release:
  1. Commit `vX.Y.Z`, bumping `version` in `pyproject.toml` and the matching entry in `uv.lock`.
  2. Publish a GitHub release. `.github/workflows/release.yml` then uploads the package to PyPI.
- GitHub Actions are pinned to commit SHAs, with a `# vX.Y.Z` comment.
