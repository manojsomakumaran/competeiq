"""Real-LLM smoke test for the catalog analyzer agent."""

from __future__ import annotations

import pytest

from competeiq.agents.catalog_agent import TracedCatalogAnalyzerAgent
from tests.it.conftest import live_only


@live_only
@pytest.mark.integration_api
def test_catalog_agent_returns_valid_pydantic(live_provider):
    agent = TracedCatalogAnalyzerAgent(provider=live_provider)
    result = agent.analyze(
        product_data=(
            "Our Products (Company X):\n"
            "  Headphones X1 - features: Bluetooth 5.0, ANC, 20h Battery, Fast Charge\n"
            "  Headphones X2 - features: Bluetooth 5.2, Advanced ANC, 30h Battery\n\n"
            "Competitor Products (Company Y):\n"
            "  Headphones Y1 - features: Bluetooth 4.2, 15h Battery\n"
            "  Headphones Y2 - features: Bluetooth 5.0, Noise Cancelling, 25h Battery"
        ),
        category="Wireless Headphones",
    )
    assert result["success"] is True, result.get("error")
    payload = result["result"]
    assert payload["category"] == "Wireless Headphones"
    for key in ("our_strengths", "competitor_strengths", "feature_gaps", "recommendations"):
        assert isinstance(payload[key], list), f"{key} must be a list"
    assert isinstance(payload["competitive_advantage"], str)
    assert 0.0 <= float(payload["confidence"]) <= 1.0
