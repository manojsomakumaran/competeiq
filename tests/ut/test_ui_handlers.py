"""Tests for UI handlers — use a stub system rather than the full facade."""

from __future__ import annotations

import pandas as pd
import pytest

from competeiq.ui.handlers import (
    analyze_category_ui,
    price_comparison_ui,
    search_products_ui,
    status_ui,
)


class _StubSystem:
    all_products = [{"category": "Wireless Headphones"}]

    def get_status(self):
        return {
            "session_id": "sid",
            "our_company": "Company X",
            "catalog": {"total_products": 2, "categories": ["Wireless Headphones"]},
            "vector_store": {"collections": ["products"], "mode": "memory"},
            "knowledge_graph": {"nodes": 10, "edges": 20},
        }

    def analyze_category(self, category):
        return {
            "summary": {
                "overall_position": "PREMIUM",
                "key_findings": ["f1"],
                "priority_actions": ["a1"],
            },
            "marketing": {"success": True, "result": {"headline": "H"}},
        }

    def search_products(self, query, n_results=5):
        return {
            "query": query,
            "result_count": 1,
            "matches": [
                {
                    "id": "p1",
                    "product_name": "Name",
                    "company": "Company X",
                    "category": "Cat",
                    "price": 9.99,
                    "availability": "In Stock",
                    "similarity": 0.9,
                    "document": "doc",
                }
            ],
        }

    def get_price_comparison(self, category):
        return pd.DataFrame(
            [
                {
                    "company": "Company X",
                    "product_name": "Name",
                    "base_price": 10.0,
                    "effective_price": 9.0,
                    "discount_pct": 10,
                    "feature_count": 3,
                    "availability": "In Stock",
                    "sku": "X-1",
                    "price_gap_vs_category_avg": -0.5,
                }
            ]
        )


@pytest.fixture()
def system():
    return _StubSystem()


@pytest.mark.unit
def test_analyze_category_empty_input(system):
    assert "select" in analyze_category_ui(system, "").lower()


@pytest.mark.unit
def test_analyze_category_happy(system):
    out = analyze_category_ui(system, "Wireless Headphones")
    assert "Category Analysis" in out
    assert "PREMIUM" in out
    assert "Marketing Headline" in out


@pytest.mark.unit
def test_search_products_empty_input(system):
    assert "enter" in search_products_ui(system, "").lower()


@pytest.mark.unit
def test_search_products_happy(system):
    out = search_products_ui(system, "foo")
    assert "Search Results" in out
    assert "Name" in out


@pytest.mark.unit
def test_price_comparison_happy(system):
    out = price_comparison_ui(system, "Wireless Headphones")
    assert "Price Comparison" in out
    assert "Name" in out


@pytest.mark.unit
def test_status_ui(system):
    out = status_ui(system)
    assert "Session ID" in out and "sid" in out
