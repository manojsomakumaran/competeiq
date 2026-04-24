# ADR-0003: Gradio for the UI, Typer for the CLI

- **Status**: Accepted
- **Date**: 2026-04-24

## Context

The project needs two entry points:

- Interactive exploration (analyst running category analyses).
- Scriptable automation (CI, pipelines, ad-hoc ops).

## Decision

- **UI**: Gradio `Blocks` with four tabs.
  - Already used in the notebook → zero-cost migration.
  - `demo.launch(share=True)` gives a public link from Colab.
  - Built-in health endpoint at `/` is ideal for ALB checks.

- **CLI**: Typer (`typer.Typer`).
  - Auto-generated `--help`.
  - Native `Annotated[...]` support keeps signatures clean.
  - First-class subcommand groups via `app.add_typer(...)` for
    `datasets` and `graph`.

## Consequences

### Positive
- Two entry points, one codebase: UI handlers are pure functions
  (`ui/handlers.py`) that take a `system` argument — CLI can reuse them
  trivially.
- `competeiq` and `competeiq-ui` console scripts in `pyproject.toml`.
- Gradio's FastAPI backend lets us add `/healthz` or `/metrics` later.

### Negative
- Gradio updates occasionally break Blocks API; we pin `gradio>=4.44,<5`.
- Typer's Click underlayer can be clumsy for streaming output; acceptable
  for this project scope.

### Revisit
If the UI grows complex (auth, multi-user state), consider replacing the
Gradio shell with a React frontend served by the same FastAPI app,
keeping `ui/handlers.py` as the shared business layer.
