"""Build the Gradio Blocks app from a stub system; assert tabs exist."""

from __future__ import annotations

import pandas as pd
import pytest

from competeiq.ui.gradio_app import build_app


class _StubSystem:
    all_products = [
        {"category": "Wireless Headphones", "company": "Company X"},
        {"category": "Smart Watches", "company": "Company X"},
    ]

    def get_status(self):
        return {
            "session_id": "ui-it",
            "our_company": "Company X",
            "components": {},
            "catalog": {
                "total_products": 2,
                "categories": ["Smart Watches", "Wireless Headphones"],
            },
            "vector_store": {"collections": ["products"], "mode": "memory"},
            "knowledge_graph": {"nodes": 1, "edges": 1},
        }

    def analyze_category(self, category):  # pragma: no cover
        return {
            "summary": {"overall_position": "PREMIUM", "key_findings": [], "priority_actions": []},
            "marketing": {"success": False},
        }

    def search_products(self, query, n_results=5):  # pragma: no cover
        return {"query": query, "result_count": 0, "matches": []}

    def get_price_comparison(self, category):  # pragma: no cover
        return pd.DataFrame()


@pytest.mark.integration_ui
def test_gradio_app_builds_with_four_tabs():
    app = build_app(_StubSystem())
    # Gradio's Blocks expose a config dict containing block info.
    config = app.config if hasattr(app, "config") else {}
    text = repr(config)
    for tab in ("Category Analysis", "Product Search", "Price Comparison", "System Status"):
        assert tab in text, f"missing tab '{tab}' in built app"
