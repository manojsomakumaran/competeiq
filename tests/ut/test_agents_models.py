import pytest
from pydantic import ValidationError

from competeiq.agents.models import FeatureAnalysis, MarketingContent, PriceAnalysis


@pytest.mark.unit
def test_price_analysis_confidence_bounds():
    with pytest.raises(ValidationError):
        PriceAnalysis(
            category="x",
            our_avg_price=10.0,
            competitor_avg_price=10.0,
            price_position="COMPETITIVE",
            price_gap_pct=0.0,
            recommendations=[],
            confidence=1.5,
        )


@pytest.mark.unit
def test_feature_analysis_accepts_empty_lists():
    obj = FeatureAnalysis(
        category="x",
        our_strengths=[],
        competitor_strengths=[],
        feature_gaps=[],
        competitive_advantage="none",
        recommendations=[],
        confidence=0.5,
    )
    assert obj.confidence == 0.5


@pytest.mark.unit
def test_marketing_content_requires_fields():
    with pytest.raises(ValidationError):
        MarketingContent(product_name="p")  # missing required fields
