"""Price monitor agent."""

from __future__ import annotations

from typing import Any

from competeiq.agents._base import build_chain
from competeiq.agents.models import PriceAnalysis
from competeiq.tracing.langfuse_client import LangfuseProvider


class TracedPriceMonitorAgent:
    """Analyze competitor pricing and emit a structured :class:`PriceAnalysis`."""

    SYSTEM_MESSAGE = """\
You are a competitive pricing intelligence analyst.
Your job is to compare our product pricing against a competitor's within a single category.

Pricing position rules:
  - PREMIUM     : our average price is more than 10% higher than the competitor
  - COMPETITIVE : our average price is within +/-10% of the competitor
  - VALUE       : our average price is more than 10% lower than the competitor

Consider price elasticity, value perception, and discount strategies.
Provide concrete, actionable pricing recommendations.

{format_instructions}"""

    HUMAN_TEMPLATE = (
        "Category: {category}\n\nProduct pricing data:\n{product_data}\n\n"
        "Analyze the pricing and return a structured PriceAnalysis."
    )

    def __init__(self, model: str = "gpt-4o-mini", provider: LangfuseProvider | None = None):
        self.model = model
        self.provider = provider

    def analyze(self, product_data: str, category: str = "unknown") -> dict[str, Any]:
        try:
            chain, parser = build_chain(
                model=self.model,
                temperature=0.0,
                trace_name=f"price-agent-{category}",
                tags=["price-agent", "week-4"],
                system_message=self.SYSTEM_MESSAGE,
                human_template=self.HUMAN_TEMPLATE,
                output_model=PriceAnalysis,
                provider=self.provider,
            )
            result: PriceAnalysis = chain.invoke(
                {
                    "category": category,
                    "product_data": product_data,
                    "format_instructions": parser.get_format_instructions(),
                }
            )
            return {"success": True, "result": result.model_dump()}
        except Exception as exc:
            return {"success": False, "error": str(exc)}
