"""Render the knowledge graph to PNG."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from competeiq.graph.visualize import draw_graph  # noqa: E402
from competeiq.system import EcommerceIntelligenceSystem  # noqa: E402


def main() -> None:
    system = EcommerceIntelligenceSystem.build_default()
    out = draw_graph(system.knowledge_graph.graph, "product_knowledge_graph.png")
    print(f"Saved graph to {out}")


if __name__ == "__main__":
    main()
