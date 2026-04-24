# Configuration

All configuration flows through `competeiq.config.Settings`, a
`pydantic-settings.BaseSettings` that resolves values in this priority order:

1. Constructor arguments
2. Process environment variables
3. `.env` file (discovery order below)
4. Google Colab `userdata` (when running in Colab)
5. Field defaults

## `.env` discovery order

When `Settings.load()` runs it walks these locations, stopping at the first
existing `.env` file:

1. Current working directory (`./.env`)
2. The directory of `competeiq.config` and its ancestors up to the repo root
3. CWD parent chain up to the filesystem root
4. Colab candidates (only when `environment.is_colab()` is true):
   - `/content/drive/MyDrive/.env`
   - `/content/drive/MyDrive/CompeteIQ/.env`
   - `/content/drive/MyDrive/Colab Notebooks/.env`
   - `/content/drive/MyDrive/pwc-agenticai-capstone/.env`
   - `/content/drive/MyDrive/Agentic AI/.env`

## Required variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI secret for embeddings + chat completions |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key |

## Optional variables

| Variable | Default | Description |
|---|---|---|
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Langfuse endpoint |
| `OPENAI_CHAT_MODEL` | `gpt-4o-mini` | Chat model |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `COMPETEIQ_DATA_DIR` | `./datasets` | Where catalog JSON lives |
| `COMPETEIQ_CHROMA_DIR` | `./.chroma` | Persistent vector-store directory |
| `COMPETEIQ_CHROMA_MODE` | `persistent` | `persistent` \| `memory` |
| `COMPETEIQ_OUR_COMPANY` | `Company X` | Which catalog represents "our" products |
| `COMPETEIQ_LOG_LEVEL` | `INFO` | Python logging level |
| `COMPETEIQ_SESSION_PREFIX` | `competeiq` | Prefix for generated session IDs |
| `GRADIO_SERVER_NAME` | `127.0.0.1` | UI bind host |
| `GRADIO_SERVER_PORT` | `7860` | UI port |
| `GRADIO_SHARE` | `false` | Create a gradio.live share link |

## Example `.env`

See [`.env.example`](../.env.example) at the repo root.

```
OPENAI_API_KEY=sk-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com

COMPETEIQ_DATA_DIR=./datasets
COMPETEIQ_CHROMA_DIR=./.chroma
COMPETEIQ_CHROMA_MODE=persistent
COMPETEIQ_OUR_COMPANY=Company X
COMPETEIQ_LOG_LEVEL=INFO
```

## Tests + CI

Unit tests never read a real `.env` — they set dummy values via pytest
fixtures (see `tests/ut/conftest.py::settings`).  CI workflows inject dummy
env vars so `Settings()` construction succeeds; live calls are mocked.
