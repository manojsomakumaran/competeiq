"""Real-LLM smoke test for the marketing content agent."""

from __future__ import annotations

import pytest

from competeiq.agents.marketing_agent import TracedMarketingAgent
from tests.it.conftest import live_only


@live_only
@pytest.mark.integration_api
def test_marketing_agent_returns_valid_pydantic(live_provider):
    agent = TracedMarketingAgent(provider=live_provider)
    result = agent.generate(
        product_data="Headphones X1, $99.99, 4 features (Bluetooth 5.0, ANC, 20h Battery)",
        competitor_data="Headphones Y1, $79.99, 3 features (Bluetooth 4.2, 15h Battery)",
        product_name="Headphones X1",
    )
    assert result["success"] is True, result.get("error")
    payload = result["result"]
    assert payload["product_name"] == "Headphones X1"
    assert isinstance(payload["headline"], str) and payload["headline"]
    assert isinstance(payload["key_benefits"], list) and payload["key_benefits"]
    assert isinstance(payload["competitive_claims"], list)
    assert isinstance(payload["target_audience"], str) and payload["target_audience"]
    assert isinstance(payload["call_to_action"], str) and payload["call_to_action"]
    assert 0.0 <= float(payload["confidence"]) <= 1.0
