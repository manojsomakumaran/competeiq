# Development Guide

## Prerequisites
- Python 3.11 or 3.12
- git
- (optional) Docker Desktop for container workflows
- (optional) GitHub CLI (`gh`) for Project/issue management

## Setup

```powershell
git clone https://github.com/manojsomakumaran/competeiq.git
cd competeiq
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Windows
# source .venv/bin/activate           # macOS / Linux
pip install -r requirements/base.txt -r requirements/dev.txt
pre-commit install
```

### Install-free testing

`pytest.ini` sets `pythonpath = src` and `tests/conftest.py` pre-pends
`src/` defensively, so you can run the full unit suite **without**
`pip install`.  This matches the user requirement "no dependency to install
package during development".

```
pytest -m unit
```

## Coding conventions

- **Formatting + linting**: `ruff` (replaces black + flake8 + isort).
  `ruff format` and `ruff check` must be clean before PR.
- **Types**: `mypy` on `src/competeiq` (currently non-blocking in CI;
  tightened over time).
- **Tests**: every new module ships with unit tests; integration tests are
  optional and must use the `integration_api` / `integration_ui` markers.
- **Commits**: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`,
  `test:`). Squash-merge PRs.
- **Branches**: `feat/<topic>`, `fix/<topic>`, `docs/<topic>`.
- **Pydantic**: agent outputs are Pydantic models; never return raw dicts
  from `.analyze()`/`.generate()`.
- **Tracing**: every public agent/orchestrator method emits a Langfuse
  span; new methods should do the same via `provider.langfuse.trace(...)`.

## Useful Make targets

```
make install            # pip-sync to dev requirements
make lint               # ruff check + format --check + mypy
make test-ut            # pytest -m unit
make test-it            # pytest -m integration_api
make ui                 # competeiq-ui
make clean              # remove build artefacts
```

## Running the notebook locally

The original `Colab-Project/CompeteIQ.ipynb` still works as a reference.
`competeiq.environment.is_colab()` and `Settings.load()` make the package
run identically in both environments.

## Repository layout

```
competeiq/
├── src/competeiq/        # library
├── tests/
│   ├── ut/               # unit tests (mocked)
│   └── it/               # integration tests (live API / UI, gated)
├── scripts/              # standalone helper scripts
├── datasets/             # catalog JSON files (generated)
├── deploy/               # Dockerfile, compose, AWS assets
├── docs/                 # this documentation
├── .github/              # workflows, issue templates
├── .gitlab-ci.yml
├── pyproject.toml
├── pytest.ini
├── Makefile
└── requirements/
```
