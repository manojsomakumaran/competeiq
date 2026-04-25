"""Index a small catalog into in-memory Chroma using real embeddings."""

from __future__ import annotations

import pytest

from competeiq.data.catalogs import COMPANY_X_CATALOG, COMPANY_Y_CATALOG
from competeiq.data.processor import TracedProductCatalogProcessor
from competeiq.embeddings.vector_store import TracedProductVectorStore
from tests.it.conftest import live_only


@live_only
@pytest.mark.integration_api
def test_index_and_search_returns_expected_category(live_provider):
    processor = TracedProductCatalogProcessor(provider=live_provider)
    products = []
    for catalog in (COMPANY_X_CATALOG, COMPANY_Y_CATALOG):
        products.extend(processor.process_catalog(catalog))

    store = TracedProductVectorStore(mode="memory", provider=live_provider)
    store.index_products_with_tracing(products, "it-products")

    results = store.search_with_tracing(
        "wireless headphones with noise cancelling",
        collection_name="it-products",
        n_results=3,
    )
    metadatas = (results.get("metadatas") or [[]])[0]
    assert metadatas, "no metadatas returned"

    categories = [m.get("category") for m in metadatas]
    assert (
        "Wireless Headphones" in categories
    ), f"expected Wireless Headphones in top results, got {categories}"
