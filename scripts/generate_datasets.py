"""Thin wrapper around :func:`competeiq.data.generator.generate_all`."""

from __future__ import annotations

import sys
from pathlib import Path

# Enable running this script directly without installing the package.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from competeiq.data.generator import generate_all  # noqa: E402


def main() -> None:
    out_dir = Path("./datasets")
    paths = generate_all(out_dir, seed=42)
    for p in paths:
        print(f"wrote {p}")


if __name__ == "__main__":
    main()
