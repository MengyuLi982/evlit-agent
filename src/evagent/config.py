from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from pydantic import Field
    from pydantic_settings import BaseSettings, SettingsConfigDict
except Exception:  # pragma: no cover - optional dependency fallback
    BaseSettings = None  # type: ignore[assignment]
    Field = None  # type: ignore[assignment]
    SettingsConfigDict = None  # type: ignore[assignment]


def _load_env_file(path: str = ".env") -> dict[str, str]:
    env_map: dict[str, str] = {}
    p = Path(path)
    if not p.exists():
        return env_map

    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key:
            env_map[key] = value
    return env_map


if BaseSettings is not None:
    class Settings(BaseSettings):
        model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

        chat_model: str = Field(default="qwen3-max", alias="EVAGENT_CHAT_MODEL")
        embed_model: str = Field(default="text-embedding-v3", alias="EVAGENT_EMBED_MODEL")

        api_key: str | None = Field(default=None, alias="EVAGENT_API_KEY")
        api_base: str | None = Field(default=None, alias="EVAGENT_API_BASE")

        dashscope_api_key: str | None = Field(default=None, alias="DASHSCOPE_API_KEY")
        dashscope_api_base: str | None = Field(default=None, alias="DASHSCOPE_API_BASE")

        s2_api_key: str | None = Field(default=None, alias="S2_API_KEY")
        openalex_api_key: str | None = Field(default=None, alias="OPENALEX_API_KEY")
        crossref_mailto: str | None = Field(default=None, alias="CROSSREF_MAILTO")

        qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
        grobid_url: str = Field(default="http://localhost:8070", alias="GROBID_URL")

        runs_dir: Path = Field(default=Path("runs"), alias="EVAGENT_RUNS_DIR")
        cache_dir: Path = Field(default=Path(".cache/evagent"), alias="EVAGENT_CACHE_DIR")
        log_level: str = Field(default="INFO", alias="EVAGENT_LOG_LEVEL")

        @property
        def effective_api_key(self) -> str | None:
            return self.api_key or self.dashscope_api_key

        @property
        def effective_api_base(self) -> str | None:
            return self.api_base or self.dashscope_api_base


    def get_settings() -> Settings:
        return Settings()
else:
    @dataclass(slots=True)
    class Settings:
        chat_model: str = "qwen3-max"
        embed_model: str = "text-embedding-v3"
        api_key: str | None = None
        api_base: str | None = None
        dashscope_api_key: str | None = None
        dashscope_api_base: str | None = None
        s2_api_key: str | None = None
        openalex_api_key: str | None = None
        crossref_mailto: str | None = None
        qdrant_url: str = "http://localhost:6333"
        grobid_url: str = "http://localhost:8070"
        runs_dir: Path = Path("runs")
        cache_dir: Path = Path(".cache/evagent")
        log_level: str = "INFO"

        @property
        def effective_api_key(self) -> str | None:
            return self.api_key or self.dashscope_api_key

        @property
        def effective_api_base(self) -> str | None:
            return self.api_base or self.dashscope_api_base


    def get_settings() -> Settings:
        env = _load_env_file(".env")
        env.update(os.environ)
        return Settings(
            chat_model=env.get("EVAGENT_CHAT_MODEL", "qwen3-max"),
            embed_model=env.get("EVAGENT_EMBED_MODEL", "text-embedding-v3"),
            api_key=env.get("EVAGENT_API_KEY"),
            api_base=env.get("EVAGENT_API_BASE"),
            dashscope_api_key=env.get("DASHSCOPE_API_KEY"),
            dashscope_api_base=env.get("DASHSCOPE_API_BASE"),
            s2_api_key=env.get("S2_API_KEY"),
            openalex_api_key=env.get("OPENALEX_API_KEY"),
            crossref_mailto=env.get("CROSSREF_MAILTO"),
            qdrant_url=env.get("QDRANT_URL", "http://localhost:6333"),
            grobid_url=env.get("GROBID_URL", "http://localhost:8070"),
            runs_dir=Path(env.get("EVAGENT_RUNS_DIR", "runs")),
            cache_dir=Path(env.get("EVAGENT_CACHE_DIR", ".cache/evagent")),
            log_level=env.get("EVAGENT_LOG_LEVEL", "INFO"),
        )
