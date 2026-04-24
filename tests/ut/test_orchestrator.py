"""Orchestrator tests with mocked agents and fake provider."""

from __future__ import annotations

import pytest

from competeiq.orchestration.orchestrator import TracedCompetitiveIntelligenceOrchestrator


class _StubPriceAgent:
    def analyze(self, text, category):
        return {
            "success": True,
            "result": {
                "price_position": "COMPETITIVE",
                "price_gap_pct": 2.0,
                "recommendations": ["price-rec"],
            },
        }


class _StubCatalogAgent:
    def analyze(self, text, category):
        return {
            "success": True,
            "result": {
                "competitive_advantage": "design",
                "feature_gaps": [],
                "our_strengths": ["a"],
                "recommendations": ["cat-rec"],
            },
        }


class _StubMarketingAgent:
    def generate(self, *, product_data, competitor_data, product_name):
        return {"success": True, "result": {"headline": f"{product_name} rocks"}}


@pytest.fixture()
def orchestrator(fake_provider, sample_products):
    our = [p for p in sample_products if p["company"] == "Company X"]
    comp = [p for p in sample_products if p["company"] == "Company Y"]
    return TracedCompetitiveIntelligenceOrchestrator(
        products_ours=our,
        products_competitor=comp,
        price_agent=_StubPriceAgent(),
        catalog_agent=_StubCatalogAgent(),
        marketing_agent=_StubMarketingAgent(),
        provider=fake_provider,
    )


@pytest.mark.unit
def test_prepare_category_data_rejects_missing_category(orchestrator):
    with pytest.raises(ValueError):
        orchestrator.prepare_category_data("Nonexistent")


@pytest.mark.unit
def test_prepare_category_data_happy(orchestrator):
    data = orchestrator.prepare_category_data("Wireless Headphones")
    assert data["category"] == "Wireless Headphones"
    assert data["products_ours"] and data["products_competitor"]
    assert "Our Products:" in data["combined_text"]


@pytest.mark.unit
def test_analyze_category_with_tracing_creates_spans(orchestrator, fake_provider):
    result = orchestrator.analyze_category_with_tracing("Wireless Headphones")
    assert result["summary"]["overall_position"] == "COMPETITIVE"
    assert result["marketing"]["success"] is True
    trace = fake_provider.langfuse.traces[-1]
    span_names = [s.name for s in trace.spans]
    assert "parallel-analysis" in span_names
    assert "aggregate-insights" in span_names
    assert "marketing-generation" in span_names
