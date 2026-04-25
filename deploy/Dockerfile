# syntax=docker/dockerfile:1.7
# CompeteIQ — CLI runtime image.
#
# Build (from repo root):
#   docker build -f deploy/Dockerfile -t competeiq:latest .
#
# Run:
#   docker run --rm --env-file .env competeiq:latest analyze "Wireless Headphones"

ARG PYTHON_VERSION=3.11

# ----------------------------- builder stage --------------------------------
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# build-essential needed for some optional native wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Install locked runtime deps first (cacheable layer)
COPY requirements/base.txt requirements/base.txt
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install --require-hashes --no-deps -r requirements/base.txt

# Install the package itself (no deps; locked above)
COPY pyproject.toml README.md LICENSE ./
COPY src/ src/
RUN /opt/venv/bin/pip install --no-deps .

# ----------------------------- runtime stage --------------------------------
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    COMPETEIQ_CHROMA_MODE=persistent \
    COMPETEIQ_CHROMA_PATH=/data/.chroma

# Non-root user
RUN groupadd --system app && useradd --system --gid app --home /home/app --create-home app

WORKDIR /app

# Copy venv from builder
COPY --from=builder /opt/venv /opt/venv

# Bake datasets into the image (small, deterministic)
COPY --chown=app:app datasets/ /app/datasets/

# Persistent volume for Chroma
RUN mkdir -p /data/.chroma && chown -R app:app /data /app
VOLUME ["/data"]

USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import competeiq; print('ok')"]

ENTRYPOINT ["competeiq"]
CMD ["--help"]
