"""Pydantic models for structured agent outputs."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PriceAnalysis(BaseModel):
    """Structured output for price analysis."""

    category: str = Field(description="Product category analyzed")
    our_avg_price: float = Field(description="Our average effective price in USD")
    competitor_avg_price: float = Field(description="Competitor average effective price in USD")
    price_position: str = Field(
        description="Pricing position relative to competitor: PREMIUM, COMPETITIVE, or VALUE"
    )
    price_gap_pct: float = Field(
        description="Price gap as a percentage: positive means we are more expensive"
    )
    recommendations: list[str] = Field(description="List of actionable pricing recommendations")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence score for the analysis, between 0.0 and 1.0"
    )


class FeatureAnalysis(BaseModel):
    """Structured output for feature / catalog analysis."""

    category: str = Field(description="Product category analyzed")
    our_strengths: list[str] = Field(description="Features unique to our products")
    competitor_strengths: list[str] = Field(description="Features unique to competitor products")
    feature_gaps: list[str] = Field(description="Features we are missing that the competitor has")
    competitive_advantage: str = Field(description="Our main competitive advantage in the category")
    recommendations: list[str] = Field(description="Product development recommendations")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")


class MarketingContent(BaseModel):
    """Structured output for marketing content generation."""

    product_name: str = Field(description="Name of the product being marketed")
    headline: str = Field(description="Attention-grabbing marketing headline")
    key_benefits: list[str] = Field(description="Top benefits to highlight")
    competitive_claims: list[str] = Field(description="Defensible comparative claims")
    target_audience: str = Field(description="Target customer segment")
    call_to_action: str = Field(description="Compelling call-to-action text")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
