# CompeteIQ Documentation

Welcome to the CompeteIQ documentation.  Start here:

| Document | Purpose |
|---|---|
| [architecture.md](architecture.md) | System architecture, layers, data flow |
| [configuration.md](configuration.md) | Environment variables, `.env` resolution, Settings |
| [usage-cli.md](usage-cli.md) | `competeiq` CLI reference |
| [usage-ui.md](usage-ui.md) | Gradio web UI tour |
| [development.md](development.md) | Local setup, coding conventions, workflow |
| [testing.md](testing.md) | Test strategy, markers, running tests |
| [docker.md](docker.md) | Container images, docker-compose |
| [deployment-aws.md](deployment-aws.md) | ECS Fargate + ALB + ECR deployment |
| [observability.md](observability.md) | Langfuse tracing, logging, health checks |
| [colab-vs-local.md](colab-vs-local.md) | Notes on running in Google Colab vs local |
| [dataset-schema.md](dataset-schema.md) | Catalog JSON schema + seeding |
| [problem-statement-mapping.md](problem-statement-mapping.md) | Mapping of capstone requirements -> code |

## Architecture Decision Records
- [ADR-0001 LangChain + Pydantic for agent outputs](adr/0001-langchain-pydantic.md)
- [ADR-0002 ChromaDB as the vector store](adr/0002-chromadb.md)
- [ADR-0003 Gradio for the UI, Typer for the CLI](adr/0003-gradio-typer.md)
- [ADR-0004 Langfuse for observability](adr/0004-langfuse.md)

## Quick links
- Source: https://github.com/manojsomakumaran/competeiq
- Notebook of origin: `Colab-Project/CompeteIQ.ipynb`
- Original capstone statement: `Colab-Project/docs/CompeteIQ_Markdown.md`
