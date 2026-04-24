"""Load catalog JSON files from disk."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from competeiq.data.catalogs import DEFAULT_CATALOGS
from competeiq.data.schemas import CatalogDict

log = logging.getLogger(__name__)


def load_catalog_file(path: Path) -> CatalogDict:
    """Load a single catalog JSON file with minimal validation."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "company" not in data or "products" not in data:
        raise ValueError(f"Invalid catalog file {path}: missing 'company' or 'products'")
    return data  # type: ignore[return-value]


def load_all_catalogs(data_dir: Path | None = None) -> list[CatalogDict]:
    """Load every ``*.json`` catalog file from ``data_dir``.

    Falls back to the built-in ``DEFAULT_CATALOGS`` when the directory is
    missing or empty.
    """
    if data_dir is None or not Path(data_dir).is_dir():
        return list(DEFAULT_CATALOGS)

    catalogs: list[CatalogDict] = []
    for json_path in sorted(Path(data_dir).glob("*.json")):
        try:
            catalogs.append(load_catalog_file(json_path))
        except Exception as exc:  # noqa: BLE001
            log.warning("Skipping malformed catalog %s: %s", json_path, exc)

    return catalogs or list(DEFAULT_CATALOGS)
