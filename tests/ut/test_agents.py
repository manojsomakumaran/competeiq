"""Agent tests using a monkeypatched build_chain to avoid live LLM calls."""

from __future__ import annotations

import pytest

from competeiq.agents import catalog_agent, marketing_agent, price_agent
from competeiq.agents.models import FeatureAnalysis, MarketingContent, PriceAnalysis


class _FakeChain:
    def __init__(self, output):
        self.output = output

    def invoke(self, inputs):
        return self.output


class _FakeParser:
    def get_format_instructions(self):
        return "{}"


def _fake_build(output):
    def _builder(**kwargs):
        return _FakeChain(output), _FakeParser()
    return _builder


@pytest.fixture()
def sample_price_output():
    return PriceAnalysis(
        category="Cat",
        our_avg_price=100.0,
        competitor_avg_price=110.0,
        price_position="VALUE",
        price_gap_pct=-9.1,
        recommendations=["lower price"],
        confidence=0.8,
    )


@pytest.fixture()
def sample_feature_output():
    return FeatureAnalysis(
        category="Cat",
        our_strengths=["a"],
        competitor_strengths=["b"],
        feature_gaps=["c"],
        competitive_advantage="speed",
        recommendations=["add c"],
        confidence=0.7,
    )


@pytest.fixture()
def sample_marketing_output():
    return MarketingContent(
        product_name="P",
        headline="Great!",
        key_benefits=["fast", "cheap"],
        competitive_claims=["faster than X"],
        target_audience="everyone",
        call_to_action="Buy now",
        confidence=0.9,
    )


@pytest.mark.unit
def test_price_agent_success(monkeypatch, sample_price_output):
    monkeypatch.setattr(price_agent, "build_chain", _fake_build(sample_price_output))
    out = price_agent.TracedPriceMonitorAgent().analyze("data", "Cat")
    assert out["success"] is True
    assert out["result"]["price_position"] == "VALUE"


@pytest.mark.unit
def test_price_agent_error(monkeypatch):
    def boom(**kwargs):
        raise RuntimeError("api down")

    monkeypatch.setattr(price_agent, "build_chain", boom)
    out = price_agent.TracedPriceMonitorAgent().analyze("data", "Cat")
    assert out["success"] is False
    assert "api down" in out["error"]


@pytest.mark.unit
def test_catalog_agent_success(monkeypatch, sample_feature_output):
    monkeypatch.setattr(catalog_agent, "build_chain", _fake_build(sample_feature_output))
    out = catalog_agent.TracedCatalogAnalyzerAgent().analyze("data", "Cat")
    assert out["success"] is True
    assert out["result"]["feature_gaps"] == ["c"]


@pytest.mark.unit
def test_marketing_agent_success(monkeypatch, sample_marketing_output):
    monkeypatch.setattr(marketing_agent, "build_chain", _fake_build(sample_marketing_output))
    out = marketing_agent.TracedMarketingAgent().generate(
        product_data="p", competitor_data="c", product_name="P"
    )
    assert out["success"] is True
    assert out["result"]["headline"] == "Great!"
