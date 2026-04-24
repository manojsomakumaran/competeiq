# CompeteIQ

> **AI-Driven Multi-Agent E-Commerce Competitive Intelligence System**

Production-grade Python package for competitive intelligence in e-commerce,
built around a multi-agent architecture with full Langfuse observability.

[![CI](https://github.com/manojsomakumaran/competeiq/actions/workflows/ci.yml/badge.svg)](https://github.com/manojsomakumaran/competeiq/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

---

## Features

- **Multi-agent orchestration** — Price, Catalog, and Marketing agents coordinated in parallel
- **Semantic product search** — ChromaDB + OpenAI embeddings
- **Knowledge graph** — NetworkX-based product taxonomy with competitive relationships
- **Full observability** — every LLM call traced via Langfuse
- **Dual-environment** — runs identically in local dev and Google Colab
- **Interfaces** — Gradio web UI and Typer CLI

## Quick Start

```powershell
# Clone and set up a virtual environment
git clone https://github.com/manojsomakumaran/competeiq.git
cd competeiq
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install test deps (no package install required for testing)
pip install -r requirements/test.txt

# Run unit tests
pytest -m unit

# Install package for development
pip install -e .[dev,test]

# Configure environment
copy .env.example .env
# Edit .env with your OpenAI + Langfuse keys

# Generate datasets
competeiq datasets generate

# Launch UI
competeiq ui
```

## Project Layout

```
competeiq/
├── Colab-Project/       # Original notebooks (runs standalone, untouched)
├── src/competeiq/       # Package source
├── datasets/            # Sample catalogs (JSON)
├── tests/ut/            # Unit tests
├── tests/it/api/        # Integration tests (live LLM)
├── tests/it/ui/         # Integration tests (Gradio E2E — local only)
├── deploy/              # Docker + AWS assets
└── docs/                # Architecture, usage, deployment
```

## Documentation

- [Architecture](docs/architecture.md)
- [Configuration](docs/configuration.md)
- [CLI Usage](docs/usage-cli.md)
- [UI Usage](docs/usage-ui.md)
- [Dataset Schema](docs/dataset-schema.md)
- [Testing](docs/testing.md)
- [AWS Deployment](docs/deployment-aws.md)
- [Colab vs Local](docs/colab-vs-local.md)

## License

MIT — see [LICENSE](./LICENSE).
