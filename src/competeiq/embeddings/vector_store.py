"""ChromaDB-backed product vector store with Langfuse tracing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from competeiq.data.schemas import NormalizedProduct
from competeiq.tracing.langfuse_client import LangfuseProvider, get_provider
from competeiq.tracing.traced_llm import traced_embedding


class TracedProductVectorStore:
    """Semantic product search via ChromaDB + OpenAI embeddings."""

    def __init__(
        self,
        *,
        mode: str = "persistent",
        persist_dir: Path | str | None = None,
        provider: LangfuseProvider | None = None,
        client: Any | None = None,
    ) -> None:
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        self._provider = provider
        self.mode = mode
        if client is not None:
            self.client = client
        elif mode == "persistent":
            persist_path = Path(persist_dir or "./.chroma")
            persist_path.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=str(persist_path),
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        else:
            self.client = chromadb.Client(ChromaSettings(anonymized_telemetry=False))
        self.collections: dict[str, Any] = {}

    # ---------------- text rendering ----------------

    def create_product_text(self, product: NormalizedProduct | dict[str, Any]) -> str:
        product_name = product.get("product_name", "")
        category = product.get("category", "")
        price = product.get("effective_price", product.get("base_price", 0))
        features = product.get("features", [])
        company = product.get("company", "")
        features_str = ", ".join(features) if features else "None"
        return (
            f"{product_name}. "
            f"Company: {company}. "
            f"Category: {category}. "
            f"Price: ${price}. "
            f"Features: {features_str}."
        )

    # ---------------- indexing ----------------

    def index_products_with_tracing(
        self,
        products: list[NormalizedProduct],
        collection_name: str = "products",
    ) -> None:
        provider = self._provider or get_provider()
        collection = self.client.get_or_create_collection(collection_name)
        self.collections[collection_name] = collection

        trace = provider.langfuse.trace(
            name=f"vector-store-indexing-{collection_name}",
            session_id=provider.session_id,
            tags=["vector-store", "indexing", "week-3"],
            metadata={"collection": collection_name, "product_count": len(products)},
        )

        ids, embeddings, documents, metadatas = [], [], [], []
        for product in products:
            rec_id = product.get("product_id") or product.get("sku", "")
            text = self.create_product_text(product)
            embedding = traced_embedding(
                text, trace_name=f"embed-{rec_id}", provider=provider
            )
            metadata = {
                "product_id": rec_id,
                "product_name": product.get("product_name", ""),
                "company": product.get("company", ""),
                "category": product.get("category", ""),
                "price": str(product.get("effective_price", 0)),
                "availability": product.get("availability", ""),
                "sku": product.get("sku", ""),
            }
            ids.append(rec_id)
            embeddings.append(embedding)
            documents.append(text)
            metadatas.append(metadata)

        collection.add(
            ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
        )
        trace.update(output={"indexed_count": len(ids), "collection": collection_name})

    # ---------------- search ----------------

    def search_with_tracing(
        self,
        query: str,
        *,
        collection_name: str = "products",
        n_results: int = 5,
    ) -> dict[str, Any]:
        if collection_name not in self.collections:
            raise ValueError(
                f"Collection '{collection_name}' not found. Index products first."
            )

        provider = self._provider or get_provider()
        collection = self.collections[collection_name]

        trace = provider.langfuse.trace(
            name="vector-store-search",
            session_id=provider.session_id,
            tags=["vector-store", "search", "week-3"],
            metadata={
                "query": query,
                "collection": collection_name,
                "n_results": n_results,
            },
        )

        query_embedding = traced_embedding(
            query, trace_name="embed-query", provider=provider
        )
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        top_results = []
        if results.get("metadatas") and results["metadatas"][0]:
            top_results = [
                {
                    "product_name": m.get("product_name"),
                    "company": m.get("company"),
                    "distance": round(d, 4),
                }
                for m, d in zip(results["metadatas"][0], results["distances"][0])
            ]
        trace.update(output={"top_results": top_results})
        return results
