"""Shared fixtures for integration tests.

These tests use **real** OpenAI + Langfuse credentials.  They are skipped
when those env vars are missing, so the suite is safe to run in any
environment.
"""

from __future__ import annotations

import contextlib

import pytest

from competeiq.config import Settings
from competeiq.tracing import langfuse_client as _lf
from competeiq.tracing.langfuse_client import build_provider


def _have_live_keys() -> bool:
    """Return True when all live secrets resolve via Settings.load()."""
    try:
        s = Settings.load()
    except Exception:
        return False
    return all(
        (
            getattr(s, "openai_api_key", "") or "",
            getattr(s, "langfuse_secret_key", "") or "",
            getattr(s, "langfuse_public_key", "") or "",
        )
    ) and not any(
        v.startswith("ci-dummy") or v.startswith("test-")
        for v in (
            s.openai_api_key,
            s.langfuse_secret_key,
            s.langfuse_public_key,
        )
    )


live_only = pytest.mark.skipif(
    not _have_live_keys(),
    reason="Live OpenAI/Langfuse credentials not configured.",
)


@pytest.fixture(scope="session")
def live_settings() -> Settings:
    return Settings.load()


@pytest.fixture(scope="session")
def live_provider(live_settings):
    """Real Langfuse + OpenAI provider for the whole session."""
    provider = build_provider(live_settings)
    _lf.set_provider(provider)
    yield provider
    with contextlib.suppress(Exception):
        provider.langfuse.flush()
    _lf.set_provider(None)
