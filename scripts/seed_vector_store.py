"""Build the persistent ChromaDB index from all catalog files."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from competeiq.config import Settings  # noqa: E402
from competeiq.logging_setup import configure_logging  # noqa: E402
from competeiq.system import EcommerceIntelligenceSystem  # noqa: E402


def main() -> None:
    settings = Settings.load()
    configure_logging(settings.log_level)
    system = EcommerceIntelligenceSystem.build_default(settings=settings)
    print(f"Indexed {len(system.all_products)} products to "
          f"{settings.chroma_dir} ({settings.chroma_mode}).")


if __name__ == "__main__":
    main()
