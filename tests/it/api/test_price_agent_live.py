"""Real-LLM smoke test for the price monitor agent."""

from __future__ import annotations

import pytest

from competeiq.agents.price_agent import TracedPriceMonitorAgent
from tests.it.conftest import live_only

_VALID_POSITIONS = {"PREMIUM", "COMPETITIVE", "VALUE"}


@live_only
@pytest.mark.integration_api
def test_price_agent_returns_valid_pydantic(live_provider):
    agent = TracedPriceMonitorAgent(provider=live_provider)
    result = agent.analyze(
        product_data=(
            "Our Products (Company X):\n"
            "  Headphones X1: $99.99 (4 features)\n"
            "  Headphones X2: $129.99 (5 features)\n\n"
            "Competitor Products (Company Y):\n"
            "  Headphones Y1: $79.99 (3 features)\n"
            "  Headphones Y2: $109.99 (4 features)"
        ),
        category="Wireless Headphones",
    )
    assert result["success"] is True, result.get("error")
    payload = result["result"]
    assert payload["category"] == "Wireless Headphones"
    assert payload["price_position"] in _VALID_POSITIONS
    assert isinstance(payload["our_avg_price"], int | float)
    assert isinstance(payload["competitor_avg_price"], int | float)
    assert isinstance(payload["recommendations"], list)
    assert 0.0 <= float(payload["confidence"]) <= 1.0
