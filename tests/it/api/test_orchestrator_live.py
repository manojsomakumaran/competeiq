"""End-to-end orchestrator run with all live agents."""

from __future__ import annotations

import pytest

from competeiq.data.catalogs import COMPANY_X_CATALOG, COMPANY_Y_CATALOG
from competeiq.data.processor import TracedProductCatalogProcessor
from competeiq.orchestration.orchestrator import (
    TracedCompetitiveIntelligenceOrchestrator,
)
from tests.it.conftest import live_only


@live_only
@pytest.mark.integration_api
def test_orchestrator_full_category_analysis(live_provider):
    processor = TracedProductCatalogProcessor(provider=live_provider)
    our = processor.process_catalog(COMPANY_X_CATALOG)
    competitor = processor.process_catalog(COMPANY_Y_CATALOG)

    orchestrator = TracedCompetitiveIntelligenceOrchestrator(
        products_ours=our,
        products_competitor=competitor,
        provider=live_provider,
    )
    result = orchestrator.analyze_category_with_tracing("Wireless Headphones")

    assert result["category"] == "Wireless Headphones"
    summary = result["summary"]
    assert summary["overall_position"] in {
        "PREMIUM",
        "COMPETITIVE",
        "VALUE",
        "FEATURE_LEADER",
        "FEATURE_GAP",
        "UNKNOWN",
    }
    assert isinstance(summary["key_findings"], list)
    assert isinstance(summary["priority_actions"], list)

    # At least one of price/catalog must have succeeded for a healthy run.
    analyses = result["analyses"]
    assert analyses["price_analysis"]["success"] or analyses["catalog_analysis"]["success"]
