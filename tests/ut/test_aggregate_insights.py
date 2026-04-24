"""Rule-matrix tests for TracedCompetitiveIntelligenceOrchestrator._aggregate_insights."""

from __future__ import annotations

import pytest

from competeiq.orchestration.orchestrator import TracedCompetitiveIntelligenceOrchestrator


@pytest.fixture()
def orchestrator(fake_provider, sample_products):
    our = [p for p in sample_products if p["company"] == "Company X"]
    comp = [p for p in sample_products if p["company"] == "Company Y"]
    return TracedCompetitiveIntelligenceOrchestrator(
        products_ours=our, products_competitor=comp, provider=fake_provider
    )


@pytest.mark.unit
def test_both_success_position_from_price(orchestrator):
    analyses = {
        "price_analysis": {
            "success": True,
            "result": {
                "price_position": "PREMIUM",
                "price_gap_pct": 15.0,
                "recommendations": ["recA", "recB"],
            },
        },
        "catalog_analysis": {
            "success": True,
            "result": {
                "competitive_advantage": "feature depth",
                "feature_gaps": [],
                "our_strengths": ["x"],
                "recommendations": ["recB", "recC"],  # recB duplicates
            },
        },
    }
    out = orchestrator._aggregate_insights(analyses)
    assert out["overall_position"] == "PREMIUM"
    assert out["priority_actions"] == ["recA", "recB", "recC"]
    assert out["analysis_success"] == {"price": True, "catalog": True}


@pytest.mark.unit
def test_price_fail_catalog_feature_leader(orchestrator):
    analyses = {
        "price_analysis": {"success": False, "error": "timeout"},
        "catalog_analysis": {
            "success": True,
            "result": {
                "competitive_advantage": "edge",
                "feature_gaps": [],
                "our_strengths": ["a", "b"],
                "recommendations": [],
            },
        },
    }
    out = orchestrator._aggregate_insights(analyses)
    assert out["overall_position"] == "FEATURE_LEADER"
    assert any("Price analysis failed" in f for f in out["key_findings"])


@pytest.mark.unit
def test_price_fail_catalog_feature_gap(orchestrator):
    analyses = {
        "price_analysis": {"success": False, "error": "timeout"},
        "catalog_analysis": {
            "success": True,
            "result": {
                "competitive_advantage": "",
                "feature_gaps": ["IP67", "USB-C"],
                "our_strengths": [],
                "recommendations": ["add IP67"],
            },
        },
    }
    out = orchestrator._aggregate_insights(analyses)
    assert out["overall_position"] == "FEATURE_GAP"
    assert any("Key feature gaps" in f for f in out["key_findings"])


@pytest.mark.unit
def test_both_fail_unknown(orchestrator):
    analyses = {
        "price_analysis": {"success": False, "error": "err1"},
        "catalog_analysis": {"success": False, "error": "err2"},
    }
    out = orchestrator._aggregate_insights(analyses)
    assert out["overall_position"] == "UNKNOWN"
    assert len([f for f in out["key_findings"] if "failed" in f]) == 2


@pytest.mark.unit
def test_priority_actions_dedup_and_top5(orchestrator):
    analyses = {
        "price_analysis": {
            "success": True,
            "result": {
                "price_position": "COMPETITIVE",
                "price_gap_pct": 0.0,
                "recommendations": ["a", "b", "c", "d"],
            },
        },
        "catalog_analysis": {
            "success": True,
            "result": {
                "competitive_advantage": "x",
                "feature_gaps": [],
                "our_strengths": [],
                "recommendations": ["d", "e", "f", "g", "h"],  # d duplicates
            },
        },
    }
    out = orchestrator._aggregate_insights(analyses)
    assert out["priority_actions"] == ["a", "b", "c", "d", "e"]
