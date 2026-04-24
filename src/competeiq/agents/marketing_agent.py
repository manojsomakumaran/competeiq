"""Marketing copy generation agent."""

from __future__ import annotations

from typing import Any

from competeiq.agents._base import build_chain
from competeiq.agents.models import MarketingContent
from competeiq.tracing.langfuse_client import LangfuseProvider


class TracedMarketingAgent:
    """Generate competitive marketing content for a specific product."""

    SYSTEM_MESSAGE = """\
You are an expert marketing copywriter specialising in consumer electronics.
Your job is to create compelling, competitive marketing content for a specific product.

Guidelines:
  - Lead with customer benefits, not just technical features
  - Write an attention-grabbing headline that differentiates us from competitors
  - Make only credible, factually defensible comparative claims
  - Use engaging, action-oriented language throughout
  - Identify the most relevant target customer segment
  - End with a clear, compelling call-to-action

{format_instructions}"""

    HUMAN_TEMPLATE = (
        "Product to market: {product_name}\n\n"
        "Our product details:\n{product_data}\n\n"
        "Competitor product details:\n{competitor_data}\n\n"
        "Generate compelling marketing content and return a structured MarketingContent."
    )

    def __init__(self, model: str = "gpt-4o-mini", provider: LangfuseProvider | None = None):
        self.model = model
        self.provider = provider

    def generate(
        self,
        *,
        product_data: str,
        competitor_data: str,
        product_name: str = "product",
    ) -> dict[str, Any]:
        try:
            chain, parser = build_chain(
                model=self.model,
                temperature=0.7,
                trace_name=f"marketing-agent-{product_name}",
                tags=["marketing-agent", "week-4"],
                system_message=self.SYSTEM_MESSAGE,
                human_template=self.HUMAN_TEMPLATE,
                output_model=MarketingContent,
                provider=self.provider,
            )
            result: MarketingContent = chain.invoke(
                {
                    "product_name": product_name,
                    "product_data": product_data,
                    "competitor_data": competitor_data,
                    "format_instructions": parser.get_format_instructions(),
                }
            )
            return {"success": True, "result": result.model_dump()}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": str(exc)}
