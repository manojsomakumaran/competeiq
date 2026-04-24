"""Traced OpenAI wrappers and LangChain callback handler factory."""

from __future__ import annotations

from typing import Any

from competeiq.tracing.langfuse_client import LangfuseProvider, get_provider


def traced_embedding(
    text: str,
    *,
    trace_name: str = "embedding",
    metadata: dict[str, Any] | None = None,
    provider: LangfuseProvider | None = None,
    model: str = "text-embedding-3-small",
) -> list[float]:
    """Generate an embedding with a full Langfuse trace + generation span."""
    provider = provider or get_provider()
    trace = provider.langfuse.trace(
        name=trace_name,
        session_id=provider.session_id,
        metadata=metadata or {},
    )
    generation = trace.generation(name="openai-embedding", model=model, input=text)
    response = provider.openai.embeddings.create(input=[text], model=model)  # type: ignore[attr-defined]
    embedding = response.data[0].embedding
    usage = {
        "promptTokens": getattr(response.usage, "prompt_tokens", 0) if response.usage else 0,
        "completionTokens": 0,
        "totalTokens": getattr(response.usage, "total_tokens", 0) if response.usage else 0,
    }
    generation.end(output=embedding, usage=usage)
    return embedding


def traced_completion(
    prompt: str,
    *,
    system: str = "",
    trace_name: str = "completion",
    model: str = "gpt-4o-mini",
    temperature: float = 0.0,
    metadata: dict[str, Any] | None = None,
    provider: LangfuseProvider | None = None,
) -> str:
    """Generate a chat completion with a full Langfuse trace + generation span."""
    provider = provider or get_provider()
    trace = provider.langfuse.trace(
        name=trace_name,
        session_id=provider.session_id,
        metadata={
            "operation": "competeiq_completion",
            "model": model,
            "temperature": temperature,
            "prompt_length": len(prompt),
            "has_system": bool(system),
            **(metadata or {}),
        },
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]
    generation = trace.generation(
        name="openai-chat-completion",
        model=model,
        input=messages,
        model_parameters={"temperature": temperature, "max_tokens": None},
    )
    response = provider.openai.chat.completions.create(  # type: ignore[attr-defined]
        model=model,
        messages=messages,
        temperature=temperature,
    )
    completion_text = response.choices[0].message.content
    generation.end(
        output=completion_text,
        usage={
            "promptTokens": getattr(response.usage, "prompt_tokens", 0) if response.usage else 0,
            "completionTokens": getattr(response.usage, "completion_tokens", 0)
            if response.usage
            else 0,
            "totalTokens": getattr(response.usage, "total_tokens", 0) if response.usage else 0,
        },
    )
    return completion_text


def get_langfuse_handler(
    *,
    trace_name: str,
    tags: list[str] | None = None,
    provider: LangfuseProvider | None = None,
):
    """Return a LangChain callback handler bound to the current session."""
    from langfuse.callback import CallbackHandler

    provider = provider or get_provider()
    return CallbackHandler(
        secret_key=provider.settings.langfuse_secret_key,
        public_key=provider.settings.langfuse_public_key,
        host=provider.settings.langfuse_host,
        session_id=provider.session_id,
        trace_name=trace_name,
        tags=tags or [],
    )
