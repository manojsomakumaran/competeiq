"""Configuration & settings for CompeteIQ.

Resolution order for each key:
  1. explicit argument override
  2. environment variable (already in ``os.environ``)
  3. ``.env`` file discovered by walking:
       - current working directory
       - the repo root (ancestor of this file)
       - parents of CWD
       - in Colab: common Google Drive candidates
  4. in Colab: ``google.colab.userdata.get(key)`` fallback
  5. sensible default (or raise for required keys)
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Iterable

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from competeiq.environment import IN_COLAB

# ----------------------------------------------------------------------------
# .env discovery
# ----------------------------------------------------------------------------

_DEFAULT_COLAB_ENV_CANDIDATES: tuple[str, ...] = (
    "/content/drive/MyDrive/.env",
    "/content/drive/MyDrive/CompeteIQ/.env",
    "/content/drive/MyDrive/Colab Notebooks/.env",
    "/content/drive/MyDrive/pwc-agenticai-capstone/.env",
    "/content/drive/MyDrive/Agentic AI/.env",
)


def _candidate_env_paths() -> Iterable[Path]:
    """Yield .env paths to try in priority order."""
    cwd = Path.cwd()
    yield cwd / ".env"

    # Walk up from this module to find a repo root (contains pyproject.toml)
    here = Path(__file__).resolve()
    for parent in [*here.parents][:6]:
        candidate = parent / ".env"
        if candidate not in (cwd / ".env",):
            yield candidate

    # Walk up from CWD
    for parent in cwd.parents:
        yield parent / ".env"

    if IN_COLAB:
        for p in _DEFAULT_COLAB_ENV_CANDIDATES:
            yield Path(p)


def discover_env_file() -> Path | None:
    """Return the first existing .env path from the candidate list."""
    seen: set[Path] = set()
    for path in _candidate_env_paths():
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        if path.is_file():
            return path
    return None


def _load_colab_userdata(keys: Iterable[str]) -> None:
    """Populate os.environ from Colab userdata for any missing keys."""
    if not IN_COLAB:
        return
    try:
        from google.colab import userdata  # type: ignore[import-not-found]
    except ImportError:
        return
    for key in keys:
        if os.environ.get(key):
            continue
        try:
            value = userdata.get(key)
        except Exception:
            continue
        if value:
            os.environ[key] = value


# ----------------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------------


class Settings(BaseSettings):
    """Unified runtime settings loaded from environment + .env."""

    model_config = SettingsConfigDict(
        env_file=None,  # we handle discovery manually
        env_prefix="",
        case_sensitive=True,
        extra="ignore",
    )

    # Required
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    langfuse_secret_key: str = Field(..., alias="LANGFUSE_SECRET_KEY")
    langfuse_public_key: str = Field(..., alias="LANGFUSE_PUBLIC_KEY")
    langfuse_host: str = Field(
        default="https://us.cloud.langfuse.com", alias="LANGFUSE_HOST"
    )

    # Paths
    data_dir: Path = Field(default=Path("./datasets"), alias="COMPETEIQ_DATA_DIR")
    chroma_dir: Path = Field(default=Path("./.chroma"), alias="COMPETEIQ_CHROMA_DIR")
    chroma_mode: str = Field(default="persistent", alias="COMPETEIQ_CHROMA_MODE")

    # Runtime
    session_prefix: str = Field(default="competeiq", alias="COMPETEIQ_SESSION_PREFIX")
    log_level: str = Field(default="INFO", alias="COMPETEIQ_LOG_LEVEL")
    our_company: str = Field(default="Company X", alias="COMPETEIQ_OUR_COMPANY")

    # Gradio
    gradio_share: bool = Field(default=False, alias="GRADIO_SHARE")
    gradio_server_name: str = Field(default="127.0.0.1", alias="GRADIO_SERVER_NAME")
    gradio_server_port: int = Field(default=7860, alias="GRADIO_SERVER_PORT")

    # ---------------- Factory ----------------

    @classmethod
    def load(cls, *, env_file: Path | None = None, **overrides: object) -> "Settings":
        """Load settings, performing .env discovery + Colab userdata fallback."""
        target = env_file if env_file and Path(env_file).is_file() else discover_env_file()
        if target is not None:
            try:
                from dotenv import load_dotenv
            except ImportError:  # pragma: no cover
                pass
            else:
                load_dotenv(str(target), override=False)

        _load_colab_userdata(
            [
                "OPENAI_API_KEY",
                "LANGFUSE_SECRET_KEY",
                "LANGFUSE_PUBLIC_KEY",
                "LANGFUSE_HOST",
            ]
        )

        return cls(**overrides)  # type: ignore[arg-type]

    # ---------------- Helpers ----------------

    def new_session_id(self) -> str:
        """Generate a unique session id for Langfuse tracing."""
        return f"{self.session_prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    def ensure_directories(self) -> None:
        """Create required on-disk directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if self.chroma_mode == "persistent":
            self.chroma_dir.mkdir(parents=True, exist_ok=True)
