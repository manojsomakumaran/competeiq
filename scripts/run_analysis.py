"""Headless orchestration run across all discoverable categories."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from competeiq.system import EcommerceIntelligenceSystem  # noqa: E402


def main() -> None:
    system = EcommerceIntelligenceSystem.build_default()
    categories = sorted({p["category"] for p in system.products_ours})
    for category in categories:
        try:
            result = system.analyze_category(category)
            s = result["summary"]
            print(f"\n[{category}] position={s['overall_position']} "
                  f"actions={len(s['priority_actions'])}")
        except ValueError as exc:
            print(f"Skipping {category}: {exc}")


if __name__ == "__main__":
    main()
