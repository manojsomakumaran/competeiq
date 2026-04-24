"""Langfuse + OpenAI client providers (injectable for tests)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from competeiq.config import Settings


class LangfuseLike(Protocol):
    def trace(self, *args, **kwargs): ...  # pragma: no cover
    def auth_check(self) -> bool: ...  # pragma: no cover
    def flush(self) -> None: ...  # pragma: no cover


class OpenAILike(Protocol):
    embeddings: object
    chat: object


@dataclass
class LangfuseProvider:
    """Bundle of clients used by traced wrappers. Swap in tests via ``get_provider``."""

    langfuse: LangfuseLike
    openai: OpenAILike
    session_id: str
    settings: Settings


_PROVIDER: LangfuseProvider | None = None


def build_provider(settings: Settings | None = None) -> LangfuseProvider:
    """Create a fresh provider using live Langfuse + OpenAI clients."""
    from langfuse import Langfuse
    from openai import OpenAI

    settings = settings or Settings.load()
    langfuse = Langfuse(
        secret_key=settings.langfuse_secret_key,
        public_key=settings.langfuse_public_key,
        host=settings.langfuse_host,
    )
    openai_client = OpenAI(api_key=settings.openai_api_key)
    return LangfuseProvider(
        langfuse=langfuse,
        openai=openai_client,
        session_id=settings.new_session_id(),
        settings=settings,
    )


def get_provider(settings: Settings | None = None) -> LangfuseProvider:
    """Get or lazily create the process-wide provider."""
    global _PROVIDER
    if _PROVIDER is None:
        _PROVIDER = build_provider(settings)
    return _PROVIDER


def set_provider(provider: LangfuseProvider | None) -> None:
    """Override the process-wide provider (primarily for tests)."""
    global _PROVIDER
    _PROVIDER = provider
