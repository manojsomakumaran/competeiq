"""Knowledge-graph visualization helpers."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D

NODE_COLORS = {
    "PRODUCT": "#3498db",
    "CATEGORY": "#e74c3c",
    "COMPANY": "#2ecc71",
    "FEATURE": "#f39c12",
}


def draw_graph(graph: nx.DiGraph, output_path: Path | str = "product_knowledge_graph.png") -> Path:
    """Render the knowledge graph to PNG and return the output path."""
    plt.figure(figsize=(16, 12))
    node_colors = [
        NODE_COLORS.get(graph.nodes[n].get("type", "OTHER"), "#95a5a6") for n in graph.nodes()
    ]
    pos = nx.spring_layout(graph, seed=42, k=0.85)
    nx.draw_networkx_nodes(
        graph,
        pos,
        node_color=node_colors,
        node_size=1100,
        alpha=0.92,
        linewidths=0.8,
        edgecolors="white",
    )
    nx.draw_networkx_edges(
        graph, pos, arrows=True, arrowstyle="-|>", arrowsize=12, width=1.0, alpha=0.35
    )
    labels = {
        n: (d.get("name", n) if d.get("type") == "PRODUCT" else n)
        for n, d in graph.nodes(data=True)
    }
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=8, font_weight="bold")
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", label=t, markerfacecolor=c, markersize=10)
        for t, c in NODE_COLORS.items()
    ]
    plt.legend(handles=legend_elements, loc="upper left", frameon=True)
    plt.title("E-Commerce Product Knowledge Graph", fontsize=14)
    plt.axis("off")
    plt.tight_layout()
    out = Path(output_path)
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    return out
