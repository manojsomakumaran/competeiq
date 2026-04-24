"""Pure UI handler functions — take a ``system`` argument, return markdown strings."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from competeiq.system import EcommerceIntelligenceSystem


def analyze_category_ui(system: EcommerceIntelligenceSystem, category: str) -> str:
    if not category:
        return "Please select a category."
    try:
        result = system.analyze_category(category)
        summary = result.get("summary", {})
        key_findings = summary.get("key_findings", [])
        priority_actions = summary.get("priority_actions", [])
        overall_position = summary.get("overall_position", "UNKNOWN")
        findings_md = (
            "\n".join(f"- {item}" for item in key_findings)
            if key_findings
            else "- No findings returned."
        )
        actions_md = (
            "\n".join(f"- {item}" for item in priority_actions)
            if priority_actions
            else "- No actions returned."
        )
        marketing = result.get("marketing", {})
        marketing_line = ""
        if marketing.get("success") and marketing.get("result"):
            headline = marketing["result"].get("headline", "")
            if headline:
                marketing_line = f"\n\n### Marketing Headline\n{headline}"
        return (
            f"## Category Analysis: {category}\n\n"
            f"**Overall Position:** {overall_position}\n\n"
            f"### Key Findings\n{findings_md}\n\n"
            f"### Priority Actions\n{actions_md}"
            f"{marketing_line}"
        )
    except Exception as exc:
        return f"Error running analysis for '{category}': {exc}"


def search_products_ui(system: EcommerceIntelligenceSystem, query: str) -> str:
    if not query or not query.strip():
        return "Please enter a search query."
    try:
        result = system.search_products(query=query.strip(), n_results=5)
        matches = result.get("matches", [])
        if not matches:
            return f"## Search Results\n\nNo results found for '{query.strip()}'."
        lines = [f"## Search Results for: {result['query']}", ""]
        for idx, match in enumerate(matches, start=1):
            lines.append(
                f"{idx}. **{match.get('product_name', 'Unknown Product')}** "
                f"({match.get('company', 'Unknown Company')})"
            )
            lines.append(f"   - Category: {match.get('category', 'N/A')}")
            lines.append(f"   - Price: ${match.get('price', 0):.2f}")
            lines.append(f"   - Similarity: {match.get('similarity', 0):.4f}")
            lines.append(f"   - Availability: {match.get('availability', 'N/A')}")
            lines.append("")
        return "\n".join(lines).strip()
    except Exception as exc:
        return f"Error running search: {exc}"


def price_comparison_ui(system: EcommerceIntelligenceSystem, category: str) -> str:
    if not category:
        return "Please select a category."
    try:
        df = system.get_price_comparison(category)
        if df.empty:
            return f"## Price Comparison: {category}\n\nNo products found for this category."
        display = df.copy()
        display["base_price"] = display["base_price"].map(lambda x: f"${x:.2f}")
        display["effective_price"] = display["effective_price"].map(lambda x: f"${x:.2f}")
        display["price_gap_vs_category_avg"] = display["price_gap_vs_category_avg"].map(
            lambda x: f"{x:+.2f}"
        )
        return f"## Price Comparison: {category}\n\n{display.to_markdown(index=False)}"
    except Exception as exc:
        return f"Error generating price comparison for '{category}': {exc}"


def status_ui(system: EcommerceIntelligenceSystem) -> str:
    status = system.get_status()
    catalog = status["catalog"]
    vs = status["vector_store"]
    kg = status["knowledge_graph"]
    return (
        "### System Information\n\n"
        f"- **Session ID**: {status['session_id']}\n"
        f"- **Our Company**: {status['our_company']}\n"
        f"- **Total Products**: {catalog['total_products']}\n"
        f"- **Categories**: {', '.join(catalog['categories'])}\n"
        f"- **Vector Collections**: {', '.join(vs['collections']) or 'none'} "
        f"(mode: {vs['mode']})\n"
        f"- **Knowledge Graph Nodes**: {kg['nodes']}\n"
        f"- **Knowledge Graph Edges**: {kg['edges']}\n"
    )
