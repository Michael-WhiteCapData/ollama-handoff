"""Tests for the MCP tool layer, with the Ollama client swapped for a fake."""

import json

import httpx
import pytest

from ollama_handoff import prompts, server


@pytest.fixture
def captured(make_client):
    """Install a client that records the last request body, and return it."""
    box: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        box["path"] = request.url.path
        box["body"] = json.loads(request.content)
        return httpx.Response(200, json={"response": "  done  ", "message": {"content": "  done  "}})

    server.set_client(make_client(handler))
    return box


def test_ask_local_strips_output(captured):
    assert server.ask_local("hi") == "done"


def test_summarize_bakes_system_prompt(captured):
    server.summarize_local("long text", focus="errors")
    assert captured["body"]["system"] == prompts.SUMMARIZE
    assert "Focus: errors" in captured["body"]["prompt"]


def test_code_review_uses_review_prompt(captured):
    server.code_review_local("- old\n+ new")
    assert captured["body"]["system"] == prompts.CODE_REVIEW


def test_commit_message_uses_commit_prompt(captured):
    server.draft_commit_message_local("diff --git ...")
    assert captured["body"]["system"] == prompts.COMMIT_MESSAGE


def test_extract_composes_prompt(captured):
    server.extract_local("a@b.com x@y.com", "every email")
    assert captured["body"]["system"] == prompts.EXTRACT
    assert "Extract: every email" in captured["body"]["prompt"]


def test_server_info_reports_config(captured):
    info = server.server_info()
    assert "default_model" in info and "num_ctx" in info
