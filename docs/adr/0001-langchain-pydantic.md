# ADR-0001: LangChain + Pydantic for agent outputs

- **Status**: Accepted
- **Date**: 2026-04-24
- **Deciders**: @manojsomakumaran

## Context

The notebook prototype already used LangChain chains + Pydantic models for
agent outputs. We evaluated three options when productionising:

1. **Keep LangChain + Pydantic** (status quo).
2. Replace with raw OpenAI SDK + `instructor` / `json_mode` for structure.
3. Switch to LangGraph for agent orchestration.

## Decision

Keep **LangChain LCEL chains** (`ChatOpenAI | prompt | PydanticOutputParser`)
for all three agents (Price, Catalog, Marketing).

## Consequences

### Positive
- Zero rewrite of prompts / agent logic from the notebook.
- `PydanticOutputParser.get_format_instructions()` gives consistent schema
  coaching to the model.
- Compatible with the existing Langfuse callback handler
  (`langfuse.callback.CallbackHandler`).

### Negative
- LangChain's API churns across minor versions; we pin `langchain==0.3.14`
  and friends.
- Adds import-time overhead.  Mitigated by the UI/CLI only constructing
  agents lazily inside the facade.

### Revisit
If LangChain v1 breaks LCEL or if observability becomes awkward, revisit
against a thin `instructor`-based adapter in the agents package.
