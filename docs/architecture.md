# Architecture

CompeteIQ is a multi-agent competitive-intelligence system, packaged as a
Python library with two front-ends (CLI + Gradio) and fully-traced LLM
calls via Langfuse.

## Layered view

```
 ┌───────────────────────────────────────────────────────────┐
 │ Interfaces                                                │
 │   competeiq.cli (Typer)    competeiq.ui (Gradio)          │
 └──────────────────────────┬────────────────────────────────┘
                            │
 ┌──────────────────────────▼────────────────────────────────┐
 │ Facade:  competeiq.system.EcommerceIntelligenceSystem      │
 │   build_default(), analyze_category, search_products,      │
 │   get_price_comparison, get_status                         │
 └──┬────────────┬────────────┬────────────┬──────────────────┘
    │            │            │            │
    ▼            ▼            ▼            ▼
  Data        Embeddings    Agents        Graph
  (loader,    (Chroma       (Price,       (networkx
   processor, vector store) Catalog,       product
   generator)               Marketing)     taxonomy)
                                │
                                ▼
                         Orchestration
                 (TracedCompetitiveIntelligenceOrchestrator)
                                │
 ┌──────────────────────────────▼────────────────────────────┐
 │ Tracing / Settings                                        │
 │   competeiq.tracing.LangfuseProvider                      │
 │   competeiq.config.Settings  (pydantic-settings)          │
 │   competeiq.environment (Colab/Jupyter/local detection)   │
 └───────────────────────────────────────────────────────────┘
```

## Modules

| Module | Responsibility |
|---|---|
| `competeiq.config` | `Settings` (BaseSettings) + `.env` discovery across CWD/ancestors/Colab paths |
| `competeiq.environment` | `is_colab()`, `is_jupyter()`, `is_local()` |
| `competeiq.logging_setup` | Silences third-party loggers; monkeypatches `posthog.capture` |
| `competeiq.tracing.langfuse_client` | `LangfuseProvider` dataclass, `get_provider()`, `set_provider()` |
| `competeiq.tracing.traced_llm` | `traced_embedding()`, `traced_completion()`, `get_langfuse_handler()` |
| `competeiq.data.catalogs` | Built-in Company X / Company Y catalogs (notebook parity) |
| `competeiq.data.loader` | Load JSON catalogs from disk with fallback to built-ins |
| `competeiq.data.processor` | Normalize catalogs (discount parsing, feature expansion) |
| `competeiq.data.generator` | Deterministic synth of X/Y/Z/W catalogs (6 categories) |
| `competeiq.embeddings.vector_store` | `TracedProductVectorStore` over Chroma (persistent + in-mem) |
| `competeiq.agents.*` | Price / Catalog / Marketing agents (LangChain LCEL + Pydantic) |
| `competeiq.orchestration.orchestrator` | Parallel price+catalog analysis, rule-based insight aggregation, marketing handoff |
| `competeiq.graph.knowledge_graph` | `networkx.DiGraph` with `SELLS`/`IN_CATEGORY`/`HAS_FEATURE`/`COMPETES_WITH` edges |
| `competeiq.graph.visualize` | Matplotlib PNG export |
| `competeiq.analysis.eda` | DataFrame + histogram for catalog sanity checks |
| `competeiq.system` | Top-level facade (`EcommerceIntelligenceSystem.build_default`) |
| `competeiq.cli` | Typer CLI (`status`, `analyze`, `search`, `compare`, `index`, `ui`, `datasets`, `graph`) |
| `competeiq.ui` | Gradio Blocks (4 tabs) + pure handler functions |

## Data flow for `analyze_category("Wireless Headphones")`

1. Facade fetches the category slice from `products_ours` + `products_competitor`.
2. Orchestrator opens a Langfuse trace, then runs:
   - `TracedPriceMonitorAgent.analyze()` — LLM call, temp=0.0 → `PriceAnalysis`
   - `TracedCatalogAnalyzerAgent.analyze()` — LLM call, temp=0.0 → `FeatureAnalysis`

   These are run in parallel via `ThreadPoolExecutor(max_workers=2)`.
3. Rule-based `_aggregate_insights()` merges price + feature output into
   `{overall_position, key_findings[], priority_actions[]}` with top-5
   deduped actions.
4. `TracedMarketingAgent.generate()` — LLM call, temp=0.7 → `MarketingContent`.
5. Trace is flushed; a nested result dict is returned.

## Storage

- **Vector store**: `chromadb.PersistentClient` at `COMPETEIQ_CHROMA_DIR`
  (default `./.chroma`). Switches to in-memory `Client` when
  `COMPETEIQ_CHROMA_MODE=memory`.
- **Catalogs**: JSON in `COMPETEIQ_DATA_DIR` (default `./datasets`).
- **Graph**: in-process `networkx.DiGraph`; optional PNG export.
