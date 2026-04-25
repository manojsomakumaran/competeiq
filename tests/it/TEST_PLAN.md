# Integration Test Plan

**Scope**: tests that exercise real OpenAI + Langfuse + ChromaDB.  All tests
are gated by `@live_only` and skip cleanly if env vars are missing.

## Invocation

```
pytest -m integration_api                # api tests only
pytest -m integration_ui                 # local UI E2E (NOT in CI)
```

## API tests (`tests/it/api/`)

| File | Purpose |
|---|---|
| `test_embeddings_roundtrip.py` | Real OpenAI embedding via `traced_embedding`; assert vector length + non-zero |
| `test_vector_store_live.py` | Index sample products into in-memory Chroma using real embeddings; verify `search_with_tracing` returns expected category |
| `test_price_agent_live.py` | Run `TracedPriceMonitorAgent.analyze` against gpt-4o-mini; validate Pydantic shape |
| `test_catalog_agent_live.py` | Same for `TracedCatalogAnalyzerAgent` |
| `test_marketing_agent_live.py` | Same for `TracedMarketingAgent` |
| `test_orchestrator_live.py` | End-to-end orchestrator with all real agents on one category |
| `test_system_live.py` | `EcommerceIntelligenceSystem.build_default()` smoke test + `analyze_category` |

## UI tests (`tests/it/ui/`) — local-only

| File | Purpose |
|---|---|
| `test_gradio_build.py` | Build the Blocks app from a stub system; assert tabs exist |
| `test_gradio_client_e2e.py` | Launch app on a random port, drive each tab via `gradio_client` |

## Cost & speed

- Each agent test is a single LLM call (~$0.001 with gpt-4o-mini).
- Embedding tests use `text-embedding-3-small`.
- Total api suite typically ~$0.02 and < 30 s.
- UI E2E adds ~10 s for app startup + client connection.

## Environment

- Required: `OPENAI_API_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`.
- Optional: `LANGFUSE_HOST` (default `cloud.langfuse.com`).
- Tests automatically use `COMPETEIQ_CHROMA_MODE=memory` to avoid disk writes.
