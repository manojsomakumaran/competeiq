"""Smoke test the full facade against live infrastructure."""

from __future__ import annotations

import pytest

from competeiq.config import Settings
from competeiq.system import EcommerceIntelligenceSystem
from tests.it.conftest import live_only


@live_only
@pytest.mark.integration_api
def test_build_default_and_status(monkeypatch, tmp_path):
    # Force in-memory chroma so the test is hermetic.
    monkeypatch.setenv("COMPETEIQ_CHROMA_MODE", "memory")
    monkeypatch.setenv("COMPETEIQ_CHROMA_DIR", str(tmp_path / "chroma"))

    settings = Settings.load()
    system = EcommerceIntelligenceSystem.build_default(settings=settings)

    status = system.get_status()
    assert status["catalog"]["total_products"] >= 1
    assert status["catalog"]["categories"]
    assert status["knowledge_graph"]["nodes"] > 0


@live_only
@pytest.mark.integration_api
def test_analyze_category_smoke(monkeypatch, tmp_path):
    monkeypatch.setenv("COMPETEIQ_CHROMA_MODE", "memory")
    monkeypatch.setenv("COMPETEIQ_CHROMA_DIR", str(tmp_path / "chroma"))

    settings = Settings.load()
    system = EcommerceIntelligenceSystem.build_default(settings=settings)

    categories = sorted({p["category"] for p in system.products_ours})
    assert categories, "system must have at least one our-side category"
    target = "Wireless Headphones" if "Wireless Headphones" in categories else categories[0]

    result = system.analyze_category(target)
    assert result["summary"]["overall_position"]
