# Observability

## Langfuse tracing

Every public agent / orchestrator / vector-store operation emits a Langfuse
span.  Traces are grouped by a session ID generated at startup
(`<COMPETEIQ_SESSION_PREFIX>-YYYYMMDD-HHMMSS`) and surfaced in:

- `EcommerceIntelligenceSystem.get_status()["session_id"]`
- CLI `competeiq status`
- UI tab "System Status"

### Span taxonomy

| Span name | Emitted by |
|---|---|
| `catalog-processing` | `TracedProductCatalogProcessor.process_catalog_with_tracing` |
| `normalize-product-<N>` | Per-product child span |
| `embedding-batch` | `TracedProductVectorStore.index_products_with_tracing` |
| `vector-search` | `TracedProductVectorStore.search_with_tracing` |
| `price-analysis` | `TracedPriceMonitorAgent.analyze` |
| `catalog-analysis` | `TracedCatalogAnalyzerAgent.analyze` |
| `parallel-analysis` | Orchestrator wrapping both of the above |
| `aggregate-insights` | Rule-based aggregation |
| `marketing-generation` | `TracedMarketingAgent.generate` |
| `category-analysis` | Parent trace for `analyze_category_with_tracing` |

### Accessing traces

Traces are visible at `$LANGFUSE_HOST` (default `cloud.langfuse.com`) under
your project.  Use tags `category:<name>` and `session:<id>` to filter.

## Logging

`competeiq.logging_setup.configure_logging()` is called at CLI and UI entry
points. It:

1. Sets the root logger to `COMPETEIQ_LOG_LEVEL` (default `INFO`).
2. Silences noisy third-party loggers (`httpx`, `httpcore`, `openai`,
   `langchain.*`, `chromadb.*`, `urllib3`, `asyncio`, `posthog`).
3. Monkeypatches `posthog.capture` to a no-op (Chroma auto-sends telemetry
   otherwise).

## Health checks

- **Gradio**: `GET /` returns 200 when the UI is reachable.  The ALB
  target-group health-check uses this path.
- **CLI**: `competeiq status` exits 0 only if the catalog+store+graph wired
  correctly.

## Metrics (future)

Not currently wired.  Candidates: Prometheus `/metrics` via `gradio`'s FastAPI
app, OpenTelemetry → AWS X-Ray.
