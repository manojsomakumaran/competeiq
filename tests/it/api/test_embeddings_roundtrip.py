"""Round-trip a real OpenAI embedding through the traced wrapper."""

from __future__ import annotations

import pytest

from competeiq.tracing.traced_llm import traced_embedding
from tests.it.conftest import live_only


@live_only
@pytest.mark.integration_api
def test_traced_embedding_returns_nonempty_vector(live_provider):
    vector = traced_embedding(
        "Wireless noise-cancelling headphones with 30 hour battery",
        trace_name="it-embedding-smoke",
        provider=live_provider,
    )
    assert isinstance(vector, list)
    assert len(vector) >= 256
    assert any(abs(v) > 1e-6 for v in vector)


@live_only
@pytest.mark.integration_api
def test_traced_embedding_distinguishes_categories(live_provider):
    a = traced_embedding(
        "Premium wireless headphones with active noise cancelling",
        trace_name="it-embedding-a",
        provider=live_provider,
    )
    b = traced_embedding(
        "Budget kitchen blender with 5-speed motor",
        trace_name="it-embedding-b",
        provider=live_provider,
    )

    # Cosine similarity should be lower than near-duplicate texts.
    def _cos(u, v):
        s = sum(x * y for x, y in zip(u, v, strict=False))
        nu = sum(x * x for x in u) ** 0.5
        nv = sum(x * x for x in v) ** 0.5
        return s / (nu * nv) if nu and nv else 0.0

    assert _cos(a, b) < 0.85
