"""A thin, typed client for the Ollama HTTP API.

Kept deliberately small and dependency-light (just ``httpx``) and fully
injectable so the MCP tool layer can be unit-tested without a running Ollama.
"""

from __future__ import annotations

from typing import Any

import httpx

from .config import Config


class OllamaError(RuntimeError):
    """Raised when the Ollama server cannot be reached or returns an error.

    Carries a human-readable message suitable for surfacing back to the
    calling agent, rather than leaking a raw stack trace.
    """


class OllamaClient:
    """Minimal synchronous client over the Ollama ``/api`` surface."""

    def __init__(self, config: Config, client: httpx.Client | None = None) -> None:
        self._config = config
        self._client = client or httpx.Client(timeout=config.timeout_s)

    @property
    def config(self) -> Config:
        return self._config

    def _options(self) -> dict[str, Any]:
        return {"num_ctx": self._config.num_ctx}

    def generate(
        self,
        prompt: str,
        *,
        system: str | None = None,
        model: str | None = None,
    ) -> str:
        """Run a one-shot ``/api/generate`` completion and return the text."""
        payload: dict[str, Any] = {
            "model": model or self._config.default_model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": self._config.keep_alive,
            "options": self._options(),
        }
        if system:
            payload["system"] = system
        data = self._post("/api/generate", payload)
        return str(data.get("response", "")).strip()

    def chat(self, messages: list[dict[str, str]], *, model: str | None = None) -> str:
        """Run a multi-turn ``/api/chat`` completion and return the reply text."""
        payload: dict[str, Any] = {
            "model": model or self._config.default_model,
            "messages": messages,
            "stream": False,
            "keep_alive": self._config.keep_alive,
            "options": self._options(),
        }
        data = self._post("/api/chat", payload)
        return str(data.get("message", {}).get("content", "")).strip()

    def list_models(self) -> list[str]:
        """Return the names of locally available models via ``/api/tags``."""
        data = self._get("/api/tags")
        return [m["name"] for m in data.get("models", []) if "name" in m]

    # -- transport helpers ---------------------------------------------------

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            resp = self._client.post(f"{self._config.url}{path}", json=payload)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            raise OllamaError(
                f"Ollama returned {exc.response.status_code} for {path}: "
                f"{exc.response.text[:200]}"
            ) from exc
        except httpx.HTTPError as exc:
            raise OllamaError(
                f"Could not reach Ollama at {self._config.url}{path}: {exc}. "
                "Is `ollama serve` running?"
            ) from exc

    def _get(self, path: str) -> dict[str, Any]:
        try:
            resp = self._client.get(f"{self._config.url}{path}", timeout=10.0)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as exc:
            raise OllamaError(
                f"Could not reach Ollama at {self._config.url}{path}: {exc}. "
                "Is `ollama serve` running?"
            ) from exc
