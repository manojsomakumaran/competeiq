# ADR-0002: ChromaDB as the vector store

- **Status**: Accepted
- **Date**: 2026-04-24

## Context

The notebook uses ChromaDB's `PersistentClient`.  For the packaged version
we needed a vector store that works both on a developer laptop (no server)
and in Colab (writable Drive path), without external infrastructure.

Alternatives considered:

- **FAISS** — fast, but no persistence layer, no metadata filtering as
  first-class.
- **Qdrant / Weaviate / Milvus** — require a running server or Docker.
- **PGVector** — requires Postgres.

## Decision

Use `chromadb` with two modes, selected via `COMPETEIQ_CHROMA_MODE`:

- `persistent` (default): `PersistentClient(path=COMPETEIQ_CHROMA_DIR)`
- `memory`: `Client()` — for tests, Colab ephemeral sessions, and CI

`TracedProductVectorStore` wraps both and accepts a pre-built client for
dependency injection (used in unit tests).

## Consequences

### Positive
- Zero external infra needed.
- Built-in metadata filtering used by `search_products` UI.
- Both modes share the same collection API.

### Negative
- ChromaDB ships with PostHog telemetry that's noisy; we monkeypatch
  `posthog.capture` in `logging_setup`.
- Persistent storage is a local directory; scaling to multi-replica ECS
  means mounting EFS or switching providers.

### Revisit
If we scale to multi-node or require HNSW tuning beyond Chroma's defaults,
migrate to Qdrant on ECS.
