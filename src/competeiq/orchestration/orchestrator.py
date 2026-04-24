"""Multi-agent orchestrator — parallel price + catalog analysis, then marketing."""

from __future__ import annotations

import concurrent.futures
from typing import Any

from competeiq.agents.catalog_agent import TracedCatalogAnalyzerAgent
from competeiq.agents.marketing_agent import TracedMarketingAgent
from competeiq.agents.price_agent import TracedPriceMonitorAgent
from competeiq.data.schemas import NormalizedProduct
from competeiq.tracing.langfuse_client import LangfuseProvider, get_provider


class TracedCompetitiveIntelligenceOrchestrator:
    """Coordinate price, catalog, and marketing agents for a category."""

    def __init__(
        self,
        *,
        products_ours: list[NormalizedProduct],
        products_competitor: list[NormalizedProduct],
        price_agent: TracedPriceMonitorAgent | None = None,
        catalog_agent: TracedCatalogAnalyzerAgent | None = None,
        marketing_agent: TracedMarketingAgent | None = None,
        provider: LangfuseProvider | None = None,
    ) -> None:
        self.products_ours = products_ours
        self.products_competitor = products_competitor
        self.price_agent = price_agent or TracedPriceMonitorAgent(provider=provider)
        self.catalog_agent = catalog_agent or TracedCatalogAnalyzerAgent(provider=provider)
        self.marketing_agent = marketing_agent or TracedMarketingAgent(provider=provider)
        self._provider = provider

    # ---------------- data prep ----------------

    def prepare_category_data(self, category: str) -> dict[str, Any]:
        ours = [p for p in self.products_ours if p["category"] == category]
        competitor = [p for p in self.products_competitor if p["category"] == category]
        if not ours or not competitor:
            raise ValueError(f"Missing products for category: {category}")

        def _fmt(p: NormalizedProduct) -> str:
            return (
                f"- {p['product_name']}: ${p['effective_price']}, "
                f"Features: {', '.join(p['features'])}, "
                f"Availability: {p['availability']}"
            )

        lines = ["Our Products:", *[_fmt(p) for p in ours], "", "Competitor Products:"]
        lines.extend(_fmt(p) for p in competitor)

        primary = ours[0]
        primary_competitor = competitor[0]
        return {
            "category": category,
            "products_ours": ours,
            "products_competitor": competitor,
            "combined_text": "\n".join(lines),
            "primary_product": primary,
            "primary_competitor": primary_competitor,
            "product_data_text": (
                f"{primary['product_name']}: ${primary['effective_price']}, "
                f"Features: {', '.join(primary['features'])}, "
                f"Availability: {primary['availability']}"
            ),
            "competitor_data_text": (
                f"{primary_competitor['product_name']}: ${primary_competitor['effective_price']}, "
                f"Features: {', '.join(primary_competitor['features'])}, "
                f"Availability: {primary_competitor['availability']}"
            ),
        }

    # ---------------- orchestration ----------------

    def analyze_category_with_tracing(self, category: str) -> dict[str, Any]:
        category_data = self.prepare_category_data(category)
        provider = self._provider or get_provider()

        trace = provider.langfuse.trace(
            name=f"competitive-intelligence-orchestration-{category}",
            session_id=provider.session_id,
            tags=["week-5", "orchestration", category],
            metadata={
                "category": category,
                "ours_count": len(category_data["products_ours"]),
                "competitor_count": len(category_data["products_competitor"]),
            },
        )

        analyses: dict[str, Any] = {}

        parallel_span = trace.span(
            name="parallel-analysis",
            input={"category": category, "phase": "parallel-agent-analysis"},
        )
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                price_future = executor.submit(
                    self.price_agent.analyze, category_data["combined_text"], category
                )
                catalog_future = executor.submit(
                    self.catalog_agent.analyze, category_data["combined_text"], category
                )
                analyses["price_analysis"] = price_future.result()
                analyses["catalog_analysis"] = catalog_future.result()
            parallel_span.end(
                output={
                    "price_success": analyses["price_analysis"]["success"],
                    "catalog_success": analyses["catalog_analysis"]["success"],
                }
            )
        except Exception as exc:
            parallel_span.end(output={"error": str(exc)})
            raise

        aggregation_span = trace.span(
            name="aggregate-insights",
            input={"category": category, "phase": "aggregation"},
        )
        summary = self._aggregate_insights(analyses)
        aggregation_span.end(output=summary)

        marketing_span = trace.span(
            name="marketing-generation",
            input={
                "product_name": category_data["primary_product"]["product_name"],
                "category": category,
            },
        )
        marketing_result = self.marketing_agent.generate(
            product_data=category_data["product_data_text"],
            competitor_data=category_data["competitor_data_text"],
            product_name=category_data["primary_product"]["product_name"],
        )
        marketing_span.end(
            output={
                "success": marketing_result["success"],
                "product_name": category_data["primary_product"]["product_name"],
            }
        )

        result = {
            "category": category,
            "inputs": {
                "products_ours": [p["product_name"] for p in category_data["products_ours"]],
                "products_competitor": [
                    p["product_name"] for p in category_data["products_competitor"]
                ],
            },
            "analyses": analyses,
            "summary": summary,
            "marketing": marketing_result,
        }
        trace.update(
            output={
                "category": category,
                "overall_position": summary["overall_position"],
                "priority_actions": summary["priority_actions"],
            }
        )
        return result

    # ---------------- rule-based aggregation ----------------

    def _aggregate_insights(self, analyses: dict[str, Any]) -> dict[str, Any]:
        """Deterministic rule-based aggregation of price + catalog findings."""
        key_findings: list[str] = []
        priority_actions: list[str] = []
        overall_position = "UNKNOWN"

        price_analysis = analyses.get("price_analysis", {})
        catalog_analysis = analyses.get("catalog_analysis", {})

        if price_analysis.get("success"):
            price_result = price_analysis["result"]
            overall_position = price_result.get("price_position", "UNKNOWN")
            key_findings.append(
                f"Pricing position is {price_result['price_position']} "
                f"with a {price_result['price_gap_pct']}% gap versus competitor."
            )
            priority_actions.extend(price_result.get("recommendations", []))
        else:
            key_findings.append(
                f"Price analysis failed: {price_analysis.get('error', 'Unknown error')}"
            )

        if catalog_analysis.get("success"):
            catalog_result = catalog_analysis["result"]
            if catalog_result.get("competitive_advantage"):
                key_findings.append(
                    f"Primary competitive advantage: {catalog_result['competitive_advantage']}"
                )
            if catalog_result.get("feature_gaps"):
                key_findings.append(
                    "Key feature gaps: " + ", ".join(catalog_result["feature_gaps"])
                )
            priority_actions.extend(catalog_result.get("recommendations", []))

            if overall_position == "UNKNOWN":
                if catalog_result.get("our_strengths") and not catalog_result.get("feature_gaps"):
                    overall_position = "FEATURE_LEADER"
                elif catalog_result.get("feature_gaps"):
                    overall_position = "FEATURE_GAP"
        else:
            key_findings.append(
                f"Catalog analysis failed: {catalog_analysis.get('error', 'Unknown error')}"
            )

        deduped: list[str] = []
        seen: set[str] = set()
        for action in priority_actions:
            normalized = action.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                deduped.append(normalized)

        return {
            "overall_position": overall_position,
            "key_findings": key_findings,
            "priority_actions": deduped[:5],
            "analysis_success": {
                "price": price_analysis.get("success", False),
                "catalog": catalog_analysis.get("success", False),
            },
        }
