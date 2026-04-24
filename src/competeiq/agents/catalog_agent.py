"""Catalog analyzer agent."""

from __future__ import annotations

from typing import Any

from competeiq.agents._base import build_chain
from competeiq.agents.models import FeatureAnalysis
from competeiq.tracing.langfuse_client import LangfuseProvider


class TracedCatalogAnalyzerAgent:
    """Compare product features between our catalog and a competitor's."""

    SYSTEM_MESSAGE = """\
You are a product catalog competitive intelligence analyst.
Your job is to compare product features between our catalog and a competitor's
within a single product category.

Your analysis should:
  - Identify products that are missing in our catalog but present in the competitor's and vice versa
  - Identify gaps in our product lineup in the category compared to competitor that we should consider filling
  - Identify features that are unique to our products (our differentiators)
  - Identify features that are unique to the competitor (their differentiators)
  - Highlight feature gaps we should consider closing
  - Determine our primary competitive advantage
  - Provide actionable product development recommendations, pricing opportunities, or marketing angles based on the analysis

{format_instructions}"""

    HUMAN_TEMPLATE = (
        "Category: {category}\n\nProduct feature data:\n{product_data}\n\n"
        "Analyze the feature landscape and return a structured FeatureAnalysis."
    )

    def __init__(self, model: str = "gpt-4o-mini", provider: LangfuseProvider | None = None):
        self.model = model
        self.provider = provider

    def analyze(self, product_data: str, category: str = "unknown") -> dict[str, Any]:
        try:
            chain, parser = build_chain(
                model=self.model,
                temperature=0.0,
                trace_name=f"catalog-agent-{category}",
                tags=["catalog-agent", "week-4"],
                system_message=self.SYSTEM_MESSAGE,
                human_template=self.HUMAN_TEMPLATE,
                output_model=FeatureAnalysis,
                provider=self.provider,
            )
            result: FeatureAnalysis = chain.invoke(
                {
                    "category": category,
                    "product_data": product_data,
                    "format_instructions": parser.get_format_instructions(),
                }
            )
            return {"success": True, "result": result.model_dump()}
        except Exception as exc:
            return {"success": False, "error": str(exc)}
