"""Shared agent building blocks."""

from __future__ import annotations

from typing import Any

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from competeiq.tracing.langfuse_client import LangfuseProvider, get_provider
from competeiq.tracing.traced_llm import get_langfuse_handler


def build_chain(
    *,
    model: str,
    temperature: float,
    trace_name: str,
    tags: list[str],
    system_message: str,
    human_template: str,
    output_model: type[BaseModel],
    provider: LangfuseProvider | None = None,
) -> tuple[Any, PydanticOutputParser]:
    """Assemble a LangChain LCEL chain bound to the Langfuse session."""
    provider = provider or get_provider()
    parser = PydanticOutputParser(pydantic_object=output_model)
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_message), ("human", human_template)]
    )
    handler = get_langfuse_handler(trace_name=trace_name, tags=tags, provider=provider)
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        openai_api_key=provider.settings.openai_api_key,
        callbacks=[handler],
    )
    return prompt | llm | parser, parser
