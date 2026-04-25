# Docker

CompeteIQ ships two production images and a `docker-compose.yml` for local
runs. All build files live in [`deploy/`](../deploy).

## Images

| File | Image | Purpose |
|---|---|---|
| [`deploy/Dockerfile`](../deploy/Dockerfile) | `competeiq:latest` | Typer CLI runtime |
| [`deploy/Dockerfile.ui`](../deploy/Dockerfile.ui) | `competeiq-ui:latest` | Gradio web UI on `:7860` |

Both are multi-stage builds based on `python:3.11-slim-bookworm`:

1. **builder** stage installs the locked dependency set
   (`requirements/base.txt` with `--require-hashes`) into a venv at
   `/opt/venv`, then installs the package itself with `--no-deps`.
2. **runtime** stage copies the venv, drops to a non-root `app` user,
   bakes the `datasets/` tree into `/app/datasets`, mounts a persistent
   `/data` volume for ChromaDB, and sets a healthcheck.

`.dockerignore` at the repo root excludes notebooks, tests, secrets,
caches, and other non-shipping artefacts.

## Build

From the repository root:

```powershell
docker build -f deploy/Dockerfile    -t competeiq:latest    .
docker build -f deploy/Dockerfile.ui -t competeiq-ui:latest .
```

## Run

### CLI

```powershell
docker run --rm --env-file .env competeiq:latest analyze "Wireless Headphones"
```

### UI

```powershell
docker run --rm -p 7860:7860 --env-file .env competeiq-ui:latest
# open http://localhost:7860
```

### docker-compose

```powershell
docker compose -f deploy/docker-compose.yml up --build
# UI: http://localhost:7860
# CLI (ad-hoc): docker compose -f deploy/docker-compose.yml --profile cli run --rm cli analyze "Wireless Headphones"
```

The `chroma-data` named volume keeps the vector index across container
restarts.  `datasets/` is mounted read-only from the host so updates to
the catalogue do not require an image rebuild.

## Environment

`.env` is read from the project root. Required keys:

- `OPENAI_API_KEY`
- `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_HOST`

Optional overrides set by the images by default:

- `COMPETEIQ_CHROMA_MODE=persistent`
- `COMPETEIQ_CHROMA_PATH=/data/.chroma`
- (UI only) `GRADIO_SERVER_NAME=0.0.0.0`, `GRADIO_SERVER_PORT=7860`,
  `GRADIO_ANALYTICS_ENABLED=False`

## Image hygiene

- Non-root user (`app:app`) — never `root` at runtime.
- No build toolchain in the runtime layer (only the prebuilt venv).
- No secrets baked in — `.env` is mounted at runtime via `--env-file`.
- Healthchecks in both images so orchestrators can detect crashes.

See [deployment-aws.md](deployment-aws.md) for pushing these images
to ECR and running them on ECS Fargate.
