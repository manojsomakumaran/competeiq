"""Tests for EcommerceIntelligenceSystem with mocked vector store + agents."""

from __future__ import annotations

import pytest

from competeiq.data.processor import TracedProductCatalogProcessor
from competeiq.graph.knowledge_graph import ProductKnowledgeGraph
from competeiq.system import EcommerceIntelligenceSystem


class _StubVS:
    def __init__(self):
        self.collections = {"products": object()}

    def search_with_tracing(self, query, *, collection_name, n_results):
        return {
            "ids": [["p1", "p2"]],
            "documents": [["d1", "d2"]],
            "metadatas": [
                [
                    {
                        "product_name": "A",
                        "company": "Company X",
                        "category": "Wireless Headphones",
                        "price": "99.99",
                        "availability": "In Stock",
                    },
                    {
                        "product_name": "B",
                        "company": "Company Y",
                        "category": "Wireless Headphones",
                        "price": "105",
                        "availability": "In Stock",
                    },
                ]
            ],
            "distances": [[0.1, 0.2]],
        }

    def index_products_with_tracing(self, products, name):
        pass


class _StubOrch:
    def analyze_category_with_tracing(self, category):
        return {
            "category": category,
            "summary": {
                "overall_position": "PREMIUM",
                "key_findings": ["f"],
                "priority_actions": ["a"],
            },
            "marketing": {"success": True, "result": {"headline": "H"}},
        }


@pytest.fixture()
def system(fake_provider, settings, sample_products):
    our = [p for p in sample_products if p["company"] == "Company X"]
    comp = [p for p in sample_products if p["company"] == "Company Y"]
    kg = ProductKnowledgeGraph()
    for p in sample_products:
        kg.add_product(p)
    return EcommerceIntelligenceSystem(
        settings=settings,
        provider=fake_provider,
        processor=TracedProductCatalogProcessor(provider=fake_provider),
        vector_store=_StubVS(),
        orchestrator=_StubOrch(),
        knowledge_graph=kg,
        our_company="Company X",
        products_ours=our,
        products_competitor=comp,
    )


@pytest.mark.unit
def test_analyze_category_unknown_raises(system):
    with pytest.raises(ValueError):
        system.analyze_category("Nonexistent")


@pytest.mark.unit
def test_analyze_category_happy(system):
    result = system.analyze_category("Wireless Headphones")
    assert result["summary"]["overall_position"] == "PREMIUM"


@pytest.mark.unit
def test_search_products_empty_raises(system):
    with pytest.raises(ValueError):
        system.search_products("   ")


@pytest.mark.unit
def test_search_products_returns_normalized(system):
    result = system.search_products("headphones")
    assert result["result_count"] == 2
    assert 0 <= result["matches"][0]["similarity"] <= 1
    assert result["matches"][0]["price"] == 99.99


@pytest.mark.unit
def test_price_comparison_unknown_category_returns_empty(system):
    df = system.get_price_comparison("Nothing")
    assert df.empty
    assert list(df.columns)[0] == "company"


@pytest.mark.unit
def test_price_comparison_sorted_and_avg(system):
    df = system.get_price_comparison("Wireless Headphones")
    assert not df.empty
    assert "price_gap_vs_category_avg" in df.columns


@pytest.mark.unit
def test_get_status_shape(system):
    s = system.get_status()
    assert {
        "session_id",
        "our_company",
        "components",
        "catalog",
        "vector_store",
        "knowledge_graph",
    } <= s.keys()
