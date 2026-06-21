import json

import httpx
import pytest

from ollama_handoff.config import Config
from ollama_handoff.ollama import OllamaError


def test_generate_returns_stripped_response(echo_client):
    assert echo_client.generate("hello") == "GEN:hello"


def test_generate_passes_system_and_model(make_client):
    seen = {}

    def handler(request):
        seen.update(json.loads(request.content))
        return httpx.Response(200, json={"response": "ok"})

    client = make_client(handler)
    client.generate("p", system="be terse", model="custom:7b")
    assert seen["system"] == "be terse"
    assert seen["model"] == "custom:7b"
    assert seen["stream"] is False
    assert seen["options"]["num_ctx"] == Config().num_ctx


def test_chat_returns_last_reply(echo_client):
    out = echo_client.chat([{"role": "user", "content": "ping"}])
    assert out == "CHAT:ping"


def test_list_models_extracts_names(echo_client):
    assert echo_client.list_models() == ["qwen2.5-coder:14b", "llama3.1:8b"]


def test_http_status_error_becomes_ollama_error(make_client):
    client = make_client(lambda request: httpx.Response(500, text="boom"))
    with pytest.raises(OllamaError, match="500"):
        client.generate("x")


def test_connection_error_is_friendly(make_client):
    def handler(request):
        raise httpx.ConnectError("refused")

    client = make_client(handler)
    with pytest.raises(OllamaError, match="ollama serve"):
        client.list_models()
