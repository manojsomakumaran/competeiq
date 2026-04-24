"""Typer-based command-line interface."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from competeiq.config import Settings
from competeiq.logging_setup import configure_logging

app = typer.Typer(
    name="competeiq",
    help="AI-driven multi-agent e-commerce competitive intelligence.",
    add_completion=False,
    no_args_is_help=True,
)

datasets_app = typer.Typer(help="Manage sample catalog datasets.", no_args_is_help=True)
graph_app = typer.Typer(help="Knowledge-graph operations.", no_args_is_help=True)
app.add_typer(datasets_app, name="datasets")
app.add_typer(graph_app, name="graph")

console = Console()


def _build_system():
    from competeiq.system import EcommerceIntelligenceSystem

    settings = Settings.load()
    configure_logging(settings.log_level)
    return EcommerceIntelligenceSystem.build_default(settings=settings)


@app.command()
def status() -> None:
    """Print system status (products indexed, categories, KG stats)."""
    system = _build_system()
    s = system.get_status()
    table = Table(title="CompeteIQ Status", show_header=False)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value")
    table.add_row("Session ID", s["session_id"])
    table.add_row("Our Company", s["our_company"])
    table.add_row("Total Products", str(s["catalog"]["total_products"]))
    table.add_row("Categories", ", ".join(s["catalog"]["categories"]))
    table.add_row("Vector Collections", ", ".join(s["vector_store"]["collections"]) or "(none)")
    table.add_row("Vector Store Mode", s["vector_store"]["mode"])
    table.add_row("KG Nodes", str(s["knowledge_graph"]["nodes"]))
    table.add_row("KG Edges", str(s["knowledge_graph"]["edges"]))
    console.print(table)


@app.command()
def analyze(category: str = typer.Argument(..., help="Product category to analyze.")) -> None:
    """Run multi-agent competitive analysis for a category."""
    system = _build_system()
    result = system.analyze_category(category)
    summary = result["summary"]
    console.print(f"[bold]Category:[/bold] {category}")
    console.print(f"[bold]Overall Position:[/bold] {summary['overall_position']}")
    console.print("\n[bold]Key Findings:[/bold]")
    for f in summary["key_findings"]:
        console.print(f"  - {f}")
    console.print("\n[bold]Priority Actions:[/bold]")
    for a in summary["priority_actions"]:
        console.print(f"  - {a}")
    marketing = result.get("marketing", {})
    if marketing.get("success"):
        console.print(f"\n[bold]Marketing Headline:[/bold] {marketing['result']['headline']}")


@app.command()
def search(
    query: str = typer.Argument(..., help="Semantic search query."),
    n: int = typer.Option(5, "--n", help="Number of results."),
) -> None:
    """Semantic product search."""
    system = _build_system()
    result = system.search_products(query, n_results=n)
    console.print(f"[bold]Query:[/bold] {result['query']}")
    for i, m in enumerate(result["matches"], 1):
        console.print(
            f"  {i}. {m['product_name']} ({m['company']}) — "
            f"${m['price']:.2f} similarity={m['similarity']}"
        )


@app.command()
def compare(category: str = typer.Argument(..., help="Product category to compare.")) -> None:
    """Show a price-comparison table for a category."""
    system = _build_system()
    df = system.get_price_comparison(category)
    if df.empty:
        console.print(f"[yellow]No products found for category: {category}[/yellow]")
        return
    table = Table(title=f"Price Comparison — {category}")
    for col in df.columns:
        table.add_column(col)
    for _, row in df.iterrows():
        table.add_row(*[str(v) for v in row])
    console.print(table)


@app.command()
def index() -> None:
    """Rebuild the persistent vector store collection."""
    system = _build_system()
    system.vector_store.index_products_with_tracing(
        system.all_products, system.DEFAULT_COLLECTION
    )
    console.print(f"Indexed {len(system.all_products)} products.")


@app.command()
def ui(
    host: str = typer.Option("127.0.0.1", help="Server host."),
    port: int = typer.Option(7860, help="Server port."),
    share: bool = typer.Option(False, help="Create a public gradio.live share link."),
) -> None:
    """Launch the Gradio web interface."""
    from competeiq.ui.gradio_app import build_app

    system = _build_system()
    demo = build_app(system)
    result = demo.launch(
        share=share, server_name=host, server_port=port, prevent_thread_lock=False
    )
    console.print(
        f"Gradio running at http://{host}:{port}/  "
        f"(share: {getattr(result, 'share_url', None) or 'disabled'})"
    )


@datasets_app.command("generate")
def datasets_generate(
    output_dir: Path = typer.Option(
        Path("./datasets"), "--output", "-o", help="Where to write catalog JSON files."
    ),
    seed: int = typer.Option(42, "--seed", help="RNG seed for deterministic output."),
) -> None:
    """Generate the full set of sample catalogs (X, Y, Z, W) as JSON."""
    from competeiq.data.generator import generate_all

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = generate_all(output_dir, seed=seed)
    for p in paths:
        console.print(f"  wrote {p}")


@datasets_app.command("validate")
def datasets_validate(
    data_dir: Path = typer.Option(
        Path("./datasets"), "--data-dir", "-d", help="Datasets directory."
    ),
) -> None:
    """Validate all catalog JSON files against the schema."""
    from competeiq.data.loader import load_catalog_file

    ok = True
    for path in sorted(data_dir.glob("*.json")):
        try:
            cat = load_catalog_file(path)
            console.print(f"[green]OK[/green] {path.name}: {cat['company']} "
                          f"({len(cat['products'])} products)")
        except Exception as exc:  # noqa: BLE001
            ok = False
            console.print(f"[red]FAIL[/red] {path.name}: {exc}")
    if not ok:
        raise typer.Exit(code=1)


@graph_app.command("export")
def graph_export(
    output: Path = typer.Option(
        Path("./product_knowledge_graph.png"), "--output", "-o", help="PNG output path."
    ),
) -> None:
    """Render the product knowledge graph to a PNG file."""
    from competeiq.graph.visualize import draw_graph

    system = _build_system()
    out = draw_graph(system.knowledge_graph.graph, output)
    console.print(f"Saved graph to {out}")


@graph_app.command("dump")
def graph_dump() -> None:
    """Dump graph as JSON (node-link format) to stdout."""
    from networkx.readwrite import json_graph

    system = _build_system()
    console.print_json(data=json_graph.node_link_data(system.knowledge_graph.graph))


def _console_main() -> None:  # pragma: no cover
    app()


if __name__ == "__main__":  # pragma: no cover
    app()
