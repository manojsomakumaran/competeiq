# Contributing to CompeteIQ

Thanks for your interest! This document describes the contribution workflow.

## Development setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements/dev.txt -r requirements/test.txt
pip install -e .
pre-commit install
```

## Running tests

No package install is required to run unit tests — `pytest.ini` is configured
with `pythonpath=src`.

```powershell
# Unit tests only
pytest -m unit

# Integration tests against live LLMs (requires .env with API keys)
pytest -m integration_api

# UI E2E tests (local only, not in CI)
make test-it-ui
```

## Style

- Formatter: `black`
- Linter: `ruff`
- Type checker: `mypy`
- Run all checks: `make lint`
- Pre-commit enforces all of the above on `git commit`.

## Branching & PRs

1. Create a feature branch off `main`: `git checkout -b feat/short-description`
2. Commit in logical units; write descriptive messages.
3. Open a pull request; CI must be green before merge.
4. All PRs require at least one review.

## Reporting issues

Use the issue templates under `.github/ISSUE_TEMPLATE/`.
