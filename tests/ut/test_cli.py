"""CLI tests — patch _build_system to return a stub, then use Typer's CliRunner."""

from __future__ import annotations

import pandas as pd
import pytest
from typer.testing import CliRunner

from competeiq import cli


class _StubSystem:
    DEFAULT_COLLECTION = "products"
    all_products = [{"category": "Wireless Headphones"}]

    class _G:
        graph = type(
            "g", (), {"number_of_nodes": lambda self: 0, "number_of_edges": lambda self: 0}
        )()

    knowledge_graph = _G()

    class _VS:
        class _C:
            def get_or_create_collection(self, n):
                return object()

        client = _C()
        collections = {}

        def index_products_with_tracing(self, products, name):
            self.collections[name] = object()

    vector_store = _VS()

    def get_status(self):
        return {
            "session_id": "sid",
            "our_company": "Company X",
            "catalog": {"total_products": 1, "categories": ["Wireless Headphones"]},
            "vector_store": {"collections": ["products"], "mode": "memory"},
            "knowledge_graph": {"nodes": 10, "edges": 20},
        }

    def analyze_category(self, category):
        return {
            "summary": {
                "overall_position": "PREMIUM",
                "key_findings": ["f"],
                "priority_actions": ["a"],
            },
            "marketing": {"success": True, "result": {"headline": "H"}},
        }

    def search_products(self, q, n_results=5):
        return {
            "query": q,
            "matches": [
                {"product_name": "P", "company": "Company X", "price": 1.0, "similarity": 0.9}
            ],
        }

    def get_price_comparison(self, category):
        return pd.DataFrame([{"company": "Company X", "product_name": "P", "effective_price": 1.0}])


@pytest.fixture()
def runner(monkeypatch):
    monkeypatch.setattr(cli, "_build_system", lambda: _StubSystem())
    return CliRunner()


@pytest.mark.unit
def test_cli_status(runner):
    result = runner.invoke(cli.app, ["status"])
    assert result.exit_code == 0
    assert "Session ID" in result.stdout


@pytest.mark.unit
def test_cli_analyze(runner):
    result = runner.invoke(cli.app, ["analyze", "Wireless Headphones"])
    assert result.exit_code == 0
    assert "PREMIUM" in result.stdout


@pytest.mark.unit
def test_cli_search(runner):
    result = runner.invoke(cli.app, ["search", "waterproof"])
    assert result.exit_code == 0


@pytest.mark.unit
def test_cli_compare(runner):
    result = runner.invoke(cli.app, ["compare", "Wireless Headphones"])
    assert result.exit_code == 0


@pytest.mark.unit
def test_cli_index(runner):
    result = runner.invoke(cli.app, ["index"])
    assert result.exit_code == 0
    assert "Indexed" in result.stdout


@pytest.mark.unit
def test_cli_datasets_validate(tmp_path):
    # Generate valid catalogs first
    from competeiq.data.generator import generate_all

    generate_all(tmp_path, seed=42)
    runner = CliRunner()
    result = runner.invoke(cli.app, ["datasets", "validate", "-d", str(tmp_path)])
    assert result.exit_code == 0


@pytest.mark.unit
def test_cli_datasets_validate_fails_on_bad_file(tmp_path):
    (tmp_path / "bad.json").write_text("{not json", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(cli.app, ["datasets", "validate", "-d", str(tmp_path)])
    assert result.exit_code == 1
