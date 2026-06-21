"""Shared fixtures: a fake Ollama backed by httpx.MockTransport."""

from __future__ import annotations

import json
from collections.abc import Callable

import httpx
import pytest

from ollama_handoff.config import Config
from ollama_handoff.ollama import OllamaClient

Handler = Callable[[httpx.Request], httpx.Response]


@pytest.fixture
def make_client() -> Callable[[Handler], OllamaClient]:
    """Return a factory that builds an OllamaClient served by a given handler."""

    def _factory(handler: Handler) -> OllamaClient:
        http = httpx.Client(transport=httpx.MockTransport(handler))
        return OllamaClient(Config(url="http://test:11434"), client=http)

    return _factory


@pytest.fixture
def echo_client(make_client: Callable[[Handler], OllamaClient]) -> OllamaClient:
    """A client that echoes request bodies so tests can assert on payloads."""

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content) if request.content else {}
        path = request.url.path
        if path == "/api/generate":
            return httpx.Response(200, json={"response": f"GEN:{body['prompt']}"})
        if path == "/api/chat":
            last = body["messages"][-1]["content"]
            return httpx.Response(200, json={"message": {"content": f"CHAT:{last}"}})
        if path == "/api/tags":
            models = [{"name": "qwen2.5-coder:14b"}, {"name": "llama3.1:8b"}]
            return httpx.Response(200, json={"models": models})
        return httpx.Response(404, json={"error": "not found"})

    return make_client(handler)
