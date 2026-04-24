# Testing Strategy

CompeteIQ ships with three tiers of tests, selected via `pytest` markers
defined in `pytest.ini`.

| Marker | Meaning | Runs in CI? |
|---|---|---|
| `unit` | Fully mocked (no network, no real OpenAI/Langfuse/Chroma HTTP) | **Yes** (GitHub Actions + GitLab) |
| `integration_api` | Exercises real OpenAI + Langfuse with secrets | Yes (GitLab only; GitHub skips) |
| `integration_ui` | Gradio Blocks UI end-to-end via `gradio_client` | **No** — local only |
| `slow` | Long-running — opt-in only | No |

## Running

```
pytest                              # everything selected by default config
pytest -m unit                      # unit only
pytest -m integration_api           # needs .env with real keys
pytest -m "unit or integration_api"
pytest -m "unit and not slow"
pytest --collect-only               # smoke test that imports resolve
```

## Baseline

At project inception the unit suite was **77 tests passing in ~5 s** with
no install required (`pytest.ini pythonpath=src`).

## Fixtures

`tests/ut/conftest.py` provides:

| Fixture | What it gives you |
|---|---|
| `settings` | `Settings` with tmp dirs + dummy keys |
| `fake_provider` | `LangfuseProvider(langfuse=FakeLangfuse(), openai=FakeOpenAI())` installed via `set_provider()` |
| `sample_catalogs` | Built-in Company X/Y catalogs |
| `sample_products` | Normalized products from the processor |

## Writing new tests

Every new module must ship with unit tests.  Patterns in use:

- Agent tests patch `build_chain` to return a `_FakeChain` returning the
  canonical Pydantic output; exercise success + failure branches.
- Orchestrator tests stub the agent trio and assert the emitted Langfuse
  span names.
- CLI tests use `typer.testing.CliRunner` and patch `cli._build_system`.
- UI tests use a stub `system` object — no Gradio launch.

## Integration tests (Phase 6b)

- `tests/it/api/` — full agent round-trips against real APIs.  Guarded by
  presence of `OPENAI_API_KEY` + `LANGFUSE_*`; otherwise skipped.
- `tests/it/ui/` — launches Gradio on a random port and uses `gradio_client`.
  **Never runs in CI** (local-only, per project requirement).

## CI specifics

- GitHub Actions runs `pytest -m "unit and not integration_ui"` on every PR,
  plus a Python 3.11 + 3.12 matrix.
- GitLab CI adds `test-it-api` (masked secrets, `allow_failure: true`
  until the suite stabilises).
