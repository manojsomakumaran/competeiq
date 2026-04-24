# Unit Test Plan

**Scope**: pure unit tests — all external systems (OpenAI, Langfuse, ChromaDB, Gradio launch, filesystem beyond tmp_path) are mocked.  Target runtime: **< 30 s total**.

## Invocation

```
pytest -m unit
```

No package install is required — `pytest.ini` sets `pythonpath=src` and
`tests/conftest.py` adds a safety-net path insert.

## Fixtures (`tests/ut/conftest.py`)

| Fixture | Purpose |
|---|---|
| `settings` | `Settings` with test-safe env vars + tmp dirs |
| `fake_provider` | `LangfuseProvider` with `FakeLangfuse` + `FakeOpenAI`, installed as process provider |
| `sample_catalogs` | Built-in Company X/Y catalogs |
| `sample_products` | Normalized product list produced by `TracedProductCatalogProcessor` |

## Tests

### `test_environment.py`
- `is_colab` false when `google.colab` absent; true when present (monkeypatch `sys.modules`).
- `is_jupyter` false outside IPython.

### `test_config.py`
- `.env` discovery prefers CWD, falls back to repo root, walks parents.
- Missing required keys raise `ValidationError`.
- `new_session_id` formatted as `<prefix>-YYYYMMDD-HHMMSS`.
- `ensure_directories` creates data/chroma dirs only when mode=persistent.

### `test_loader.py`
- Round-trips JSON from `tmp_path`.
- Malformed files are skipped with a warning, valid ones still returned.
- Empty directory returns built-in `DEFAULT_CATALOGS`.

### `test_generator.py`
- `generate_all(tmp_path, seed=42)` writes exactly four files.
- Seed determinism: two runs with same seed produce byte-identical output.
- Every synthesized product validates against `ProductDict` contract.

### `test_processor.py`
- `parse_discount` covers: `None`, `""`, `"10% off"`, `"Free Shipping"`, `"5% off + Free Case"`, `"Free Case"`, `"Buy 1 Get 1"`.
- `normalize_features` expands `anc`, `bt`, `usb-c`, `advanced anc`.
- `normalize_product` computes correct effective_price and price_per_feature.
- `process_catalog_with_tracing` creates exactly one span per product + one trace.update.
- `compare_products` covers X-win, Y-win, tie in all three axes, plus unique/common feature sets.

### `test_vector_store.py`
- `create_product_text` snapshot-style assertion.
- `index_products_with_tracing` calls `collection.add` once with matching ids/metadatas lengths.
- `search_with_tracing` raises for unknown collection.
- Vector distances -> similarity clamping in system layer (tested in test_system).

### `test_agents_models.py`
- `PriceAnalysis.confidence` bounds enforced.
- Missing required fields raise `ValidationError`.

### `test_agents.py`
- Each agent's `.analyze`/`.generate` returns `{success: True, result: {...}}` when the chain is mocked.
- Failure path (mock chain raises) returns `{success: False, error: "..."}`.

### `test_orchestrator.py`
- `prepare_category_data` raises for missing category.
- `analyze_category_with_tracing` creates parallel + aggregate + marketing spans (mocked agents).

### `test_aggregate_insights.py` — **rule matrix**
- Both success → `overall_position` from price; findings/actions merged + deduped.
- Price fail + catalog success with strengths, no gaps → `FEATURE_LEADER`.
- Price fail + catalog success with gaps → `FEATURE_GAP`.
- Price fail + catalog fail → `UNKNOWN` with two failure findings.
- Action dedup preserves order and caps at top-5.

### `test_knowledge_graph.py`
- Taxonomy seeded; categories/companies/features nodes exist.
- `add_product` creates `SELLS`, `IN_CATEGORY`, `HAS_FEATURE` edges.
- Bidirectional `COMPETES_WITH` only across companies in same category.
- `find_competing_products` and `get_unique_features` happy + missing-node paths.

### `test_system.py`
- `build_default` wires processor/store/orchestrator/graph.
- `analyze_category` rejects unknown category.
- `search_products` rejects empty query.
- `get_price_comparison` returns schema-correct empty DataFrame for unknown category.
- `get_status` top-level shape.

### `test_ui_handlers.py`
- Happy path + empty-input + exception-path for each handler.
- Markdown output contains expected section headers.

### `test_cli.py`
- Typer `CliRunner` exits 0 for `status`, `search`, `analyze`, `compare` (system mocked).
- `datasets validate` exits 1 when a malformed file is present.
