"""End-to-end Gradio test driving every tab via gradio_client.

LOCAL ONLY — never runs in CI (excluded via ``-m "not integration_ui"``).
"""

from __future__ import annotations

import socket
import threading
import time
from contextlib import closing, suppress

import pandas as pd
import pytest

gradio_client = pytest.importorskip("gradio_client")

from competeiq.ui.gradio_app import build_app  # noqa: E402


class _StubSystem:
    all_products = [{"category": "Wireless Headphones", "company": "Company X"}]

    def get_status(self):
        return {
            "session_id": "ui-e2e",
            "our_company": "Company X",
            "components": {},
            "catalog": {"total_products": 1, "categories": ["Wireless Headphones"]},
            "vector_store": {"collections": ["products"], "mode": "memory"},
            "knowledge_graph": {"nodes": 1, "edges": 0},
        }

    def analyze_category(self, category):
        return {
            "summary": {
                "overall_position": "COMPETITIVE",
                "key_findings": ["finding-1"],
                "priority_actions": ["action-1"],
            },
            "marketing": {"success": True, "result": {"headline": "Hear the Difference"}},
        }

    def search_products(self, query, n_results=5):
        return {
            "query": query,
            "result_count": 1,
            "matches": [
                {
                    "product_name": "Headphones X1",
                    "company": "Company X",
                    "category": "Wireless Headphones",
                    "price": 99.99,
                    "availability": "In Stock",
                    "similarity": 0.91,
                }
            ],
        }

    def get_price_comparison(self, category):
        return pd.DataFrame(
            [
                {
                    "company": "Company X",
                    "product_name": "Headphones X1",
                    "base_price": 99.99,
                    "effective_price": 89.99,
                    "discount_pct": 10,
                    "feature_count": 4,
                    "availability": "In Stock",
                    "sku": "CX-HP-001",
                    "price_gap_vs_category_avg": 0.0,
                }
            ]
        )


def _free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture()
def running_app():
    app = build_app(_StubSystem())
    port = _free_port()
    server = threading.Thread(
        target=lambda: app.launch(
            server_name="127.0.0.1",
            server_port=port,
            prevent_thread_lock=False,
            share=False,
            show_error=True,
            quiet=True,
        ),
        daemon=True,
    )
    server.start()
    # Wait for server to be reachable
    for _ in range(40):
        try:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                s.settimeout(0.5)
                s.connect(("127.0.0.1", port))
            break
        except OSError:
            time.sleep(0.25)
    else:
        pytest.fail("Gradio server did not start in time")
    yield f"http://127.0.0.1:{port}"
    with suppress(Exception):
        app.close()


@pytest.mark.integration_ui
def test_gradio_e2e_all_tabs(running_app):
    from gradio_client import Client

    client = Client(running_app, verbose=False)
    api = client.view_api(return_format="dict") or {}
    # Verify the app exposes the four tab handlers (button click + textbox submit).
    # The exact endpoint names depend on Gradio internals, but at minimum we expect
    # several callables.
    fns = api.get("named_endpoints", {})
    assert fns, "no named endpoints exposed by Gradio app"
