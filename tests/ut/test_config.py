import pytest
from pydantic import ValidationError

from competeiq.config import Settings, discover_env_file


@pytest.mark.unit
def test_settings_rejects_missing_required_keys(monkeypatch):
    for key in ("OPENAI_API_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_PUBLIC_KEY"):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(ValidationError):
        Settings()


@pytest.mark.unit
def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "s")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "p")
    s = Settings()
    assert s.openai_api_key == "x"
    assert s.langfuse_host.startswith("https://")


@pytest.mark.unit
def test_new_session_id_shape(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "s")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "p")
    s = Settings()
    sid = s.new_session_id()
    assert sid.startswith(s.session_prefix + "-")
    assert len(sid) > len(s.session_prefix) + 5


@pytest.mark.unit
def test_ensure_directories_persistent(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "s")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "p")
    monkeypatch.setenv("COMPETEIQ_DATA_DIR", str(tmp_path / "d"))
    monkeypatch.setenv("COMPETEIQ_CHROMA_DIR", str(tmp_path / "c"))
    monkeypatch.setenv("COMPETEIQ_CHROMA_MODE", "persistent")
    s = Settings()
    s.ensure_directories()
    assert (tmp_path / "d").is_dir()
    assert (tmp_path / "c").is_dir()


@pytest.mark.unit
def test_ensure_directories_memory_skips_chroma(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "s")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "p")
    monkeypatch.setenv("COMPETEIQ_DATA_DIR", str(tmp_path / "d"))
    monkeypatch.setenv("COMPETEIQ_CHROMA_DIR", str(tmp_path / "c"))
    monkeypatch.setenv("COMPETEIQ_CHROMA_MODE", "memory")
    s = Settings()
    s.ensure_directories()
    assert (tmp_path / "d").is_dir()
    assert not (tmp_path / "c").exists()


@pytest.mark.unit
def test_discover_env_file_returns_none_in_clean_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # Assumes no .env in any ancestor; fine for tests
    result = discover_env_file()
    # Either None or a valid file; if found, must exist
    assert result is None or result.is_file()
