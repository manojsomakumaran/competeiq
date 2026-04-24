"""Shared fixtures: fake Langfuse + OpenAI providers, sample products, tmp chroma."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from competeiq.config import Settings
from competeiq.data.catalogs import COMPANY_X_CATALOG, COMPANY_Y_CATALOG
from competeiq.data.processor import TracedProductCatalogProcessor
from competeiq.tracing import langfuse_client as _lf
from competeiq.tracing.langfuse_client import LangfuseProvider

# ---------------- Fake Langfuse ----------------


class _FakeSpan:
    def __init__(self, name: str):
        self.name = name
        self.ended = False
        self.output: Any = None

    def end(self, output: Any = None, usage: Any = None) -> None:
        self.ended = True
        self.output = output


class _FakeTrace:
    def __init__(self, name: str):
        self.name = name
        self.spans: list[_FakeSpan] = []
        self.generations: list[_FakeSpan] = []
        self.updates: list[Any] = []

    def span(self, name: str, **kwargs) -> _FakeSpan:
        s = _FakeSpan(name)
        self.spans.append(s)
        return s

    def generation(self, name: str, **kwargs) -> _FakeSpan:
        g = _FakeSpan(name)
        self.generations.append(g)
        return g

    def update(self, **kwargs) -> None:
        self.updates.append(kwargs)


class FakeLangfuse:
    def __init__(self):
        self.traces: list[_FakeTrace] = []

    def trace(self, name: str, **kwargs) -> _FakeTrace:
        t = _FakeTrace(name)
        self.traces.append(t)
        return t

    def auth_check(self) -> bool:
        return True

    def flush(self) -> None:
        return None


# ---------------- Fake OpenAI ----------------


@dataclass
class _Usage:
    prompt_tokens: int = 5
    completion_tokens: int = 10
    total_tokens: int = 15


@dataclass
class _EmbeddingData:
    embedding: list[float]


@dataclass
class _EmbeddingResponse:
    data: list[_EmbeddingData]
    usage: _Usage = field(default_factory=_Usage)


@dataclass
class _Message:
    content: str


@dataclass
class _Choice:
    message: _Message


@dataclass
class _ChatResponse:
    choices: list[_Choice]
    usage: _Usage = field(default_factory=_Usage)


class _EmbeddingsAPI:
    def __init__(self):
        self.calls: list[dict] = []

    def create(self, *, input, model):
        self.calls.append({"input": input, "model": model})
        vec = [float(len(t)) / 100.0 for t in input[:1][0]][:8] or [0.1] * 8
        # Deterministic short vector
        return _EmbeddingResponse(data=[_EmbeddingData(embedding=[0.01, 0.02, 0.03, 0.04])])


class _ChatCompletionsAPI:
    def __init__(self):
        self.calls: list[dict] = []
        self.response_text = "stub-completion"

    def create(self, *, model, messages, temperature):
        self.calls.append({"model": model, "messages": messages, "temperature": temperature})
        return _ChatResponse(choices=[_Choice(message=_Message(content=self.response_text))])


class _ChatAPI:
    def __init__(self):
        self.completions = _ChatCompletionsAPI()


class FakeOpenAI:
    def __init__(self):
        self.embeddings = _EmbeddingsAPI()
        self.chat = _ChatAPI()


# ---------------- Fixtures ----------------


@pytest.fixture()
def settings(tmp_path, monkeypatch) -> Settings:
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "test-lf-secret")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "test-lf-public")
    monkeypatch.setenv("LANGFUSE_HOST", "https://example.invalid")
    monkeypatch.setenv("COMPETEIQ_DATA_DIR", str(tmp_path / "datasets"))
    monkeypatch.setenv("COMPETEIQ_CHROMA_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv("COMPETEIQ_CHROMA_MODE", "memory")
    s = Settings(
        OPENAI_API_KEY="test-openai",
        LANGFUSE_SECRET_KEY="test-lf-secret",
        LANGFUSE_PUBLIC_KEY="test-lf-public",
        LANGFUSE_HOST="https://example.invalid",
        COMPETEIQ_DATA_DIR=tmp_path / "datasets",
        COMPETEIQ_CHROMA_DIR=tmp_path / "chroma",
        COMPETEIQ_CHROMA_MODE="memory",
    )
    return s


@pytest.fixture()
def fake_provider(settings) -> LangfuseProvider:
    provider = LangfuseProvider(
        langfuse=FakeLangfuse(),
        openai=FakeOpenAI(),
        session_id="test-session",
        settings=settings,
    )
    _lf.set_provider(provider)
    yield provider
    _lf.set_provider(None)


@pytest.fixture()
def sample_catalogs():
    return [COMPANY_X_CATALOG, COMPANY_Y_CATALOG]


@pytest.fixture()
def sample_products(sample_catalogs, fake_provider):
    processor = TracedProductCatalogProcessor(provider=fake_provider)
    products = []
    for cat in sample_catalogs:
        products.extend(processor.process_catalog(cat))
    return products
