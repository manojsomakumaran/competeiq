"""Gradio Blocks application."""

from __future__ import annotations

import gradio as gr

from competeiq.config import Settings
from competeiq.logging_setup import configure_logging
from competeiq.system import EcommerceIntelligenceSystem
from competeiq.ui.handlers import (
    analyze_category_ui,
    price_comparison_ui,
    search_products_ui,
    status_ui,
)


def build_app(system: EcommerceIntelligenceSystem) -> gr.Blocks:
    """Construct the 4-tab Gradio Blocks app bound to ``system``."""
    categories = sorted({p["category"] for p in system.all_products if p.get("category")})
    default_cat = categories[0] if categories else None

    with gr.Blocks(title="CompeteIQ") as demo:
        gr.Markdown(
            """# CompeteIQ — E-Commerce Competitive Intelligence

Multi-agent AI system for competitive analysis with full Langfuse observability."""
        )

        with gr.Tab("Category Analysis"):
            cat = gr.Dropdown(choices=categories, label="Select Category", value=default_cat)
            btn = gr.Button("Run Category Analysis", variant="primary")
            out = gr.Markdown("Choose a category and click **Run Category Analysis**.")
            btn.click(fn=lambda c: analyze_category_ui(system, c), inputs=cat, outputs=out)

        with gr.Tab("Product Search"):
            q = gr.Textbox(label="Search Query", placeholder="e.g., waterproof speaker")
            sbtn = gr.Button("Search Products", variant="primary")
            sout = gr.Markdown("Enter a query and click **Search Products**.")
            sbtn.click(fn=lambda v: search_products_ui(system, v), inputs=q, outputs=sout)
            q.submit(fn=lambda v: search_products_ui(system, v), inputs=q, outputs=sout)

        with gr.Tab("Price Comparison"):
            pcat = gr.Dropdown(choices=categories, label="Select Category", value=default_cat)
            pbtn = gr.Button("Show Price Comparison", variant="primary")
            pout = gr.Markdown("Choose a category and click **Show Price Comparison**.")
            pbtn.click(fn=lambda c: price_comparison_ui(system, c), inputs=pcat, outputs=pout)

        with gr.Tab("System Status"):
            gr.Markdown(status_ui(system))

    return demo


def main() -> None:
    """CLI entry point for the ``competeiq-ui`` console script."""
    settings = Settings.load()
    configure_logging(settings.log_level)
    system = EcommerceIntelligenceSystem.build_default(settings=settings)
    demo = build_app(system)
    result = demo.launch(
        share=settings.gradio_share,
        server_name=settings.gradio_server_name,
        server_port=settings.gradio_server_port,
        prevent_thread_lock=False,
    )
    local_url = getattr(result, "local_url", None)
    share_url = getattr(result, "share_url", None)
    if local_url or share_url:
        print("\nGradio launch links:")
        print(f"- Local URL: {local_url or 'Not available'}")
        print(f"- Share URL: {share_url or 'Not available'}")


if __name__ == "__main__":  # pragma: no cover
    main()
