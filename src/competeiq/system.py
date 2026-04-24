"""EcommerceIntelligenceSystem — the high-level facade."""

from __future__ import annotations

from typing import Any

import pandas as pd

from competeiq.config import Settings
from competeiq.data.loader import load_all_catalogs
from competeiq.data.processor import TracedProductCatalogProcessor
from competeiq.data.schemas import NormalizedProduct
from competeiq.embeddings.vector_store import TracedProductVectorStore
from competeiq.graph.knowledge_graph import ProductKnowledgeGraph
from competeiq.orchestration.orchestrator import TracedCompetitiveIntelligenceOrchestrator
from competeiq.tracing.langfuse_client import LangfuseProvider, get_provider


class EcommerceIntelligenceSystem:
    """Top-level API: category analysis, product search, price comparison, status."""

    DEFAULT_COLLECTION = "products"

    def __init__(
        self,
        *,
        settings: Settings,
        provider: LangfuseProvider,
        processor: TracedProductCatalogProcessor,
        vector_store: TracedProductVectorStore,
        orchestrator: TracedCompetitiveIntelligenceOrchestrator,
        knowledge_graph: ProductKnowledgeGraph,
        our_company: str,
        products_ours: list[NormalizedProduct],
        products_competitor: list[NormalizedProduct],
    ) -> None:
        self.settings = settings
        self.provider = provider
        self.processor = processor
        self.vector_store = vector_store
        self.orchestrator = orchestrator
        self.knowledge_graph = knowledge_graph
        self.our_company = our_company
        self.products_ours = products_ours
        self.products_competitor = products_competitor
        self.all_products = [*products_ours, *products_competitor]

    # ---------------- factory ----------------

    @classmethod
    def build_default(
        cls,
        *,
        settings: Settings | None = None,
        provider: LangfuseProvider | None = None,
        index_products: bool = True,
    ) -> "EcommerceIntelligenceSystem":
        settings = settings or Settings.load()
        settings.ensure_directories()
        provider = provider or get_provider(settings)

        catalogs = load_all_catalogs(settings.data_dir)
        processor = TracedProductCatalogProcessor(provider=provider)
        all_products: list[NormalizedProduct] = []
        for catalog in catalogs:
            all_products.extend(processor.process_catalog(catalog))

        our = [p for p in all_products if p["company"] == settings.our_company]
        competitor = [p for p in all_products if p["company"] != settings.our_company]
        if not our:
            # Fall back: treat first catalog company as "ours"
            companies = [c["company"] for c in catalogs]
            our_name = companies[0] if companies else settings.our_company
            our = [p for p in all_products if p["company"] == our_name]
            competitor = [p for p in all_products if p["company"] != our_name]
        else:
            our_name = settings.our_company

        vector_store = TracedProductVectorStore(
            mode=settings.chroma_mode,
            persist_dir=settings.chroma_dir,
            provider=provider,
        )
        if index_products:
            try:
                vector_store.index_products_with_tracing(all_products, cls.DEFAULT_COLLECTION)
            except Exception:
                # If re-indexing into an existing persistent collection fails (duplicate ids),
                # ensure the collection reference is registered so searches still work.
                vector_store.collections[cls.DEFAULT_COLLECTION] = (
                    vector_store.client.get_or_create_collection(cls.DEFAULT_COLLECTION)
                )

        knowledge_graph = ProductKnowledgeGraph()
        for product in all_products:
            knowledge_graph.add_product(product)

        orchestrator = TracedCompetitiveIntelligenceOrchestrator(
            products_ours=our,
            products_competitor=competitor,
            provider=provider,
        )

        return cls(
            settings=settings,
            provider=provider,
            processor=processor,
            vector_store=vector_store,
            orchestrator=orchestrator,
            knowledge_graph=knowledge_graph,
            our_company=our_name,
            products_ours=our,
            products_competitor=competitor,
        )

    # ---------------- public API ----------------

    def analyze_category(self, category: str) -> dict[str, Any]:
        categories = {p["category"] for p in self.all_products}
        if category not in categories:
            raise ValueError(
                f"Unknown category '{category}'. Available: {sorted(categories)}"
            )
        return self.orchestrator.analyze_category_with_tracing(category)

    def search_products(self, query: str, n_results: int = 5) -> dict[str, Any]:
        if not query or not query.strip():
            raise ValueError("Search query must be a non-empty string.")
        results = self.vector_store.search_with_tracing(
            query.strip(),
            collection_name=self.DEFAULT_COLLECTION,
            n_results=n_results,
        )
        matches: list[dict[str, Any]] = []
        metadatas = (results.get("metadatas") or [[]])[0] or []
        documents = (results.get("documents") or [[]])[0] or []
        distances = (results.get("distances") or [[]])[0] or []
        ids = (results.get("ids") or [[]])[0] or []
        for doc_id, meta, doc, dist in zip(ids, metadatas, documents, distances):
            similarity = max(0.0, min(1.0, round(1 - float(dist), 4)))
            matches.append(
                {
                    "id": doc_id,
                    "product_name": meta.get("product_name"),
                    "company": meta.get("company"),
                    "category": meta.get("category"),
                    "price": float(meta.get("price", 0) or 0),
                    "availability": meta.get("availability"),
                    "similarity": similarity,
                    "document": doc,
                }
            )
        return {
            "query": query.strip(),
            "result_count": len(matches),
            "matches": matches,
        }

    def get_price_comparison(self, category: str) -> pd.DataFrame:
        products = [p for p in self.all_products if p["category"] == category]
        columns = [
            "company",
            "product_name",
            "base_price",
            "effective_price",
            "discount_pct",
            "feature_count",
            "availability",
            "sku",
            "price_gap_vs_category_avg",
        ]
        if not products:
            return pd.DataFrame(columns=columns)
        avg = sum(p["effective_price"] for p in products) / len(products)
        rows = [
            {
                "company": p["company"],
                "product_name": p["product_name"],
                "base_price": float(p["base_price"]),
                "effective_price": float(p["effective_price"]),
                "discount_pct": int(p["discount_pct"]),
                "feature_count": int(p["feature_count"]),
                "availability": p["availability"],
                "sku": p["sku"],
                "price_gap_vs_category_avg": round(p["effective_price"] - avg, 2),
            }
            for p in products
        ]
        return (
            pd.DataFrame(rows, columns=columns)
            .sort_values(["company", "effective_price"])
            .reset_index(drop=True)
        )

    def get_status(self) -> dict[str, Any]:
        return {
            "session_id": self.provider.session_id,
            "our_company": self.our_company,
            "components": {
                "processor": self.processor is not None,
                "vector_store": self.vector_store is not None,
                "orchestrator": self.orchestrator is not None,
                "knowledge_graph": self.knowledge_graph is not None,
            },
            "catalog": {
                "products_ours": len(self.products_ours),
                "products_competitor": len(self.products_competitor),
                "total_products": len(self.all_products),
                "categories": sorted({p["category"] for p in self.all_products}),
            },
            "vector_store": {
                "collections": sorted(self.vector_store.collections.keys()),
                "mode": self.settings.chroma_mode,
            },
            "knowledge_graph": {
                "nodes": self.knowledge_graph.graph.number_of_nodes(),
                "edges": self.knowledge_graph.graph.number_of_edges(),
            },
        }
