"""Unit tests for the vector store using a fake Chroma client."""

from __future__ import annotations

from typing import Any

import pytest

from competeiq.embeddings.vector_store import TracedProductVectorStore


class _FakeCollection:
    def __init__(self, name: str):
        self.name = name
        self.added: list[dict] = []
        self.queries: list[dict] = []

    def add(self, *, ids, embeddings, documents, metadatas):
        self.added.append(
            {
                "ids": ids,
                "embeddings": embeddings,
                "documents": documents,
                "metadatas": metadatas,
            }
        )

    def query(self, *, query_embeddings, n_results, include):
        self.queries.append(
            {"query_embeddings": query_embeddings, "n_results": n_results, "include": include}
        )
        return {
            "ids": [["p1"]],
            "documents": [["doc-text"]],
            "metadatas": [
                [{"product_name": "Test", "company": "Company X", "price": "99.99"}]
            ],
            "distances": [[0.12]],
        }


class _FakeChromaClient:
    def __init__(self):
        self.collections: dict[str, _FakeCollection] = {}

    def get_or_create_collection(self, name: str) -> _FakeCollection:
        self.collections.setdefault(name, _FakeCollection(name))
        return self.collections[name]


@pytest.fixture()
def store(fake_provider) -> TracedProductVectorStore:
    return TracedProductVectorStore(
        mode="memory", provider=fake_provider, client=_FakeChromaClient()
    )


@pytest.mark.unit
def test_create_product_text_format(store):
    text = store.create_product_text(
        {
            "product_name": "Name",
            "company": "Company X",
            "category": "Cat",
            "effective_price": 99.9,
            "features": ["a", "b"],
        }
    )
    assert "Name" in text and "Company X" in text and "Cat" in text
    assert "Features: a, b" in text


@pytest.mark.unit
def test_index_products_with_tracing(store, sample_products):
    store.index_products_with_tracing(sample_products, "products")
    assert "products" in store.collections
    collection: Any = store.collections["products"]
    assert len(collection.added) == 1
    batch = collection.added[0]
    assert len(batch["ids"]) == len(sample_products)
    assert len(batch["embeddings"]) == len(batch["ids"])


@pytest.mark.unit
def test_search_with_tracing_raises_for_missing_collection(store):
    with pytest.raises(ValueError):
        store.search_with_tracing("q", collection_name="absent")


@pytest.mark.unit
def test_search_with_tracing_returns_chroma_result(store, sample_products):
    store.index_products_with_tracing(sample_products, "products")
    result = store.search_with_tracing("headphones", collection_name="products", n_results=1)
    assert result["ids"] == [["p1"]]
    assert result["metadatas"][0][0]["company"] == "Company X"
