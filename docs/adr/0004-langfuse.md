# ADR-0004: Langfuse for LLM observability

- **Status**: Accepted
- **Date**: 2026-04-24

## Context

We need per-call tracing of LLM interactions for:

- Debugging prompt regressions.
- Cost attribution per category / session.
- Sharing reproducible traces with reviewers.

Options considered:

- **Langfuse** — already used in the notebook.
- **LangSmith** — tied to LangChain; fewer self-host options.
- **OpenTelemetry + custom collector** — more work, no LLM-native UI.

## Decision

Adopt **Langfuse** as the single tracing backend.  Wrap all agent and
vector-store operations in a central `LangfuseProvider` dataclass:

```python
@dataclass
class LangfuseProvider:
    langfuse: Langfuse
    openai: OpenAI
    session_id: str
    settings: Settings
```

- `get_provider()` / `set_provider()` give process-wide access.
- Tests replace it with a `FakeLangfuse` + `FakeOpenAI` fixture.
- Every traced method produces at least one span; orchestration methods
  produce a parent trace with named children (`parallel-analysis`,
  `aggregate-insights`, `marketing-generation`).

## Consequences

### Positive
- One backend, one dashboard.
- Trace graph matches the span taxonomy in
  [`observability.md`](../observability.md).
- Swappable: dependency-inject a different provider in tests or in Colab.

### Negative
- Langfuse SDK is still pre-1.0; we pin `langfuse==2.57.1`.
- Requires `LANGFUSE_*` env vars in all live environments; CI uses dummy
  keys and mocks.

### Revisit
If we add non-LLM observability (DB calls, Lambda timings), we may layer
OpenTelemetry underneath and export Langfuse as one of multiple sinks.
