"""NetworkX-backed product knowledge graph."""

from __future__ import annotations

from typing import Any

import networkx as nx

from competeiq.data.schemas import NormalizedProduct


class ProductKnowledgeGraph:
    """Graph of COMPANY, CATEGORY, PRODUCT, and FEATURE nodes with typed edges."""

    def __init__(self) -> None:
        self.graph: nx.DiGraph = nx.DiGraph()
        self._build_product_taxonomy()

    def _build_product_taxonomy(self) -> None:
        categories = ["Wireless Headphones", "Smart Watches", "Portable Speakers"]
        companies = ["Company X", "Company Y"]
        common_features = [
            "Bluetooth 5.0",
            "Bluetooth 5.2",
            "Noise Cancelling",
            "Advanced Noise Cancelling",
            "GPS",
            "Heart Rate",
            "Waterproof",
            "Water Resistant",
            "Foldable",
            "Sleep Tracking",
            "USB-C",
            "Quick Charge",
        ]
        for category in categories:
            self.graph.add_node(category, type="CATEGORY", label=category)
        for company in companies:
            self.graph.add_node(company, type="COMPANY", label=company)
        for feature in common_features:
            self.graph.add_node(feature, type="FEATURE", label=feature)

    def add_product(self, product: NormalizedProduct) -> None:
        product_id = product.get("product_id") or product.get("sku")
        if not product_id:
            raise ValueError("Each product must include 'product_id' or 'sku'.")

        company = product.get("company", "Unknown Company")
        category = product.get("category", "Unknown Category")
        product_name = product.get("product_name", product_id)
        price = product.get("effective_price", product.get("base_price", 0))
        features = product.get("features", [])

        if company not in self.graph:
            self.graph.add_node(company, type="COMPANY", label=company)
        if category not in self.graph:
            self.graph.add_node(category, type="CATEGORY", label=category)

        self.graph.add_node(
            product_id,
            type="PRODUCT",
            name=product_name,
            price=float(price) if price is not None else 0.0,
            company=company,
            category=category,
            sku=product.get("sku", ""),
        )

        self.graph.add_edge(company, product_id, relation="SELLS")
        self.graph.add_edge(product_id, category, relation="IN_CATEGORY")

        for feature in features:
            if feature not in self.graph:
                self.graph.add_node(feature, type="FEATURE", label=feature)
            self.graph.add_edge(product_id, feature, relation="HAS_FEATURE")

        for node_id, node_data in list(self.graph.nodes(data=True)):
            if node_id == product_id:
                continue
            if node_data.get("type") != "PRODUCT":
                continue
            if node_data.get("category") == category and node_data.get("company") != company:
                self.graph.add_edge(product_id, node_id, relation="COMPETES_WITH")
                self.graph.add_edge(node_id, product_id, relation="COMPETES_WITH")

    def find_competing_products(self, product_id: str) -> list[str]:
        if product_id not in self.graph:
            return []
        category = None
        for _, target, edge_data in self.graph.out_edges(product_id, data=True):
            if edge_data.get("relation") == "IN_CATEGORY":
                category = target
                break
        if category is None:
            return []
        competitors: set[str] = set()
        for source, _, edge_data in self.graph.in_edges(category, data=True):
            if (
                edge_data.get("relation") == "IN_CATEGORY"
                and source != product_id
                and self.graph.nodes[source].get("type") == "PRODUCT"
            ):
                competitors.add(source)
        for _, target, edge_data in self.graph.out_edges(product_id, data=True):
            if (
                edge_data.get("relation") == "COMPETES_WITH"
                and self.graph.nodes[target].get("type") == "PRODUCT"
            ):
                competitors.add(target)
        return sorted(competitors)

    def get_unique_features(self, product_id: str, competitor_id: str) -> dict[str, Any]:
        if product_id not in self.graph or competitor_id not in self.graph:
            return {"unique_to_ours": [], "unique_to_competitor": [], "common": []}
        features_ours = {
            target
            for _, target, edge_data in self.graph.out_edges(product_id, data=True)
            if edge_data.get("relation") == "HAS_FEATURE"
        }
        features_competitor = {
            target
            for _, target, edge_data in self.graph.out_edges(competitor_id, data=True)
            if edge_data.get("relation") == "HAS_FEATURE"
        }
        return {
            "unique_to_ours": sorted(features_ours - features_competitor),
            "unique_to_competitor": sorted(features_competitor - features_ours),
            "common": sorted(features_ours & features_competitor),
        }
