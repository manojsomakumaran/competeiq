"""Structured logging + third-party noise suppression."""

from __future__ import annotations

import logging
import os
import warnings


def silence_third_party() -> None:
    """Suppress noisy ChromaDB / PostHog telemetry errors."""
    os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
    os.environ.setdefault("CHROMA_TELEMETRY_DISABLED", "True")
    os.environ.setdefault("DO_NOT_TRACK", "1")
    os.environ.setdefault("CHROMA_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("POSTHOG_DISABLE", "1")

    for name in (
        "chromadb.telemetry.product.posthog",
        "chromadb.telemetry",
        "posthog",
    ):
        logging.getLogger(name).setLevel(logging.CRITICAL)

    warnings.filterwarnings("ignore", message=".*PostHog.*")
    warnings.filterwarnings("ignore", message=".*telemetry.*")

    try:
        import posthog  # type: ignore[import-not-found]
    except ImportError:
        return
    original = getattr(posthog, "capture", None)
    if original is None:
        return

    def _noop(*args, **kwargs) -> None:
        return None

    posthog.capture = _noop  # type: ignore[assignment]


def configure_logging(level: str = "INFO") -> None:
    """Configure root logging for CompeteIQ entry points."""
    silence_third_party()
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
