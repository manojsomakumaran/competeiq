# Problem-Statement Mapping

This page maps the capstone problem statement
([`Colab-Project/docs/CompeteIQ_Markdown.md`](../Colab-Project/docs/CompeteIQ_Markdown.md))
onto the code in this repository.  It exists so reviewers can verify that
no requirement was dropped during the notebook → package conversion.

| Requirement | Implementation |
|---|---|
| Competitive intelligence across multiple companies | `src/competeiq/data/catalogs.py` (X, Y) + `src/competeiq/data/generator.py` (Z, W) |
| Normalise heterogeneous catalog data | `src/competeiq/data/processor.py` (`parse_discount`, `normalize_features`, `normalize_product`) |
| Semantic product search | `src/competeiq/embeddings/vector_store.py` (`TracedProductVectorStore`) |
| Multi-agent analysis (price, catalog, marketing) | `src/competeiq/agents/{price_agent,catalog_agent,marketing_agent}.py` |
| Structured agent outputs | `src/competeiq/agents/models.py` (Pydantic `PriceAnalysis`, `FeatureAnalysis`, `MarketingContent`) |
| Parallel analysis + aggregation | `src/competeiq/orchestration/orchestrator.py` (`ThreadPoolExecutor`, rule-based `_aggregate_insights`) |
| Knowledge graph with competitor edges | `src/competeiq/graph/knowledge_graph.py` (`COMPETES_WITH`, `HAS_FEATURE`, `IN_CATEGORY`, `SELLS`) |
| Langfuse observability | `src/competeiq/tracing/*` + per-method spans on every traced class |
| Interactive UI | `src/competeiq/ui/gradio_app.py` (Gradio Blocks, 4 tabs) |
| Runnable in both Colab and local | `src/competeiq/config.py` (`.env` walk + Colab userdata) + `src/competeiq/environment.py` |
| Exploratory data analysis | `src/competeiq/analysis/eda.py` |
| Generate additional sample datasets | `src/competeiq/data/generator.py` + `scripts/generate_datasets.py` + `competeiq datasets generate` |
| Production quality | pyproject, pip-tools, Makefile, pre-commit, CODEOWNERS, PR/issue templates, CI/CD, Dockerfiles, AWS deploy assets, `docs/` |
| Tests (unit + integration) | `tests/ut/` (77 unit tests mocked) + `tests/it/{api,ui}/` (integration, UI tests local-only) |
| Install-free development | `pytest.ini pythonpath=src` + `tests/conftest.py` sys.path shim |

## Traceability to notebook cells

The notebook `Colab-Project/CompeteIQ.ipynb` was processed top-to-bottom;
every cell's logic is accounted for in one of the modules above.  The two
built-in company catalogs are preserved **verbatim** as Python constants
in `src/competeiq/data/catalogs.py` for output parity with the notebook.
