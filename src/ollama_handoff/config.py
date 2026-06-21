"""Environment-driven configuration for the ollama-handoff server."""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5-coder:14b"
DEFAULT_NUM_CTX = 32768
DEFAULT_KEEP_ALIVE = "30m"
DEFAULT_TIMEOUT_S = 600.0


@dataclass(frozen=True)
class Config:
    """Effective server configuration.

    All fields are sourced from environment variables via :meth:`from_env`,
    so the server can be configured entirely from its MCP registration block
    without code changes.
    """

    url: str = DEFAULT_URL
    default_model: str = DEFAULT_MODEL
    num_ctx: int = DEFAULT_NUM_CTX
    keep_alive: str = DEFAULT_KEEP_ALIVE
    timeout_s: float = DEFAULT_TIMEOUT_S

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Config:
        """Build a Config from environment variables.

        Args:
            env: Mapping to read from. Defaults to ``os.environ``. Injectable
                so tests don't have to mutate the real process environment.
        """
        src = os.environ if env is None else env
        return cls(
            url=src.get("OLLAMA_URL", DEFAULT_URL).rstrip("/"),
            default_model=src.get("OLLAMA_DEFAULT_MODEL", DEFAULT_MODEL),
            num_ctx=int(src.get("OLLAMA_NUM_CTX", str(DEFAULT_NUM_CTX))),
            keep_alive=src.get("OLLAMA_KEEP_ALIVE", DEFAULT_KEEP_ALIVE),
            timeout_s=float(src.get("OLLAMA_TIMEOUT_S", str(DEFAULT_TIMEOUT_S))),
        )

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable view of the configuration."""
        return {
            "ollama_url": self.url,
            "default_model": self.default_model,
            "num_ctx": self.num_ctx,
            "keep_alive": self.keep_alive,
            "timeout_s": self.timeout_s,
        }
