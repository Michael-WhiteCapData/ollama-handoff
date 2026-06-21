"""The ollama-handoff MCP server.

Registers a small set of MCP tools that hand work off to a local Ollama model.
Tool descriptions are written for the *calling agent*: they say when to pick
each tool, so the agent routes cheap work locally without being told to.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import prompts
from .config import Config
from .ollama import OllamaClient

mcp = FastMCP("ollama-handoff")

# A single shared client built from the environment. Swapped out in tests.
_client = OllamaClient(Config.from_env())


def set_client(client: OllamaClient) -> None:
    """Replace the module-level Ollama client (used by tests)."""
    global _client
    _client = client


# ---------------------------------------------------------------------------
# General-purpose handoff
# ---------------------------------------------------------------------------


@mcp.tool()
def ask_local(prompt: str, model: str | None = None, system: str | None = None) -> str:
    """Send a one-shot prompt to a local Ollama model and return the response.

    Use for any handoff where the cloud model's full reasoning isn't needed:
    drafts, boilerplate, simple extractions, formatting, quick lookups. Runs
    on the user's own GPU and consumes no cloud-LLM usage.

    Args:
        prompt: The task / question.
        model: Override the default model.
        system: Optional system prompt to shape behavior.
    """
    return _client.generate(prompt, system=system, model=model)


@mcp.tool()
def chat_local(messages: list[dict], model: str | None = None) -> str:
    """Multi-turn chat against a local Ollama model.

    Use when the handoff needs more than one turn of context. ``messages`` is
    a list of ``{"role": "user"|"assistant"|"system", "content": str}``.
    """
    return _client.chat(messages, model=model)


# ---------------------------------------------------------------------------
# Specialized handoffs — system prompt baked in so the agent doesn't restate
# it, and the description tells the agent when to prefer this over ask_local.
# ---------------------------------------------------------------------------


@mcp.tool()
def summarize_local(text: str, focus: str | None = None, model: str | None = None) -> str:
    """Summarize a block of text using the local model.

    Cheap offload for long files, logs, transcripts, or docs the cloud model
    doesn't need to fully ingest. Returns a concise structured summary.

    Args:
        text: The content to summarize. Can be very long (context window is configurable).
        focus: Optional focus hint, e.g. "errors and stack traces" or "API surface only".
    """
    return _client.generate(prompts.summarize_prompt(text, focus), system=prompts.SUMMARIZE, model=model)


@mcp.tool()
def code_review_local(diff_or_code: str, model: str | None = None) -> str:
    """Quick first-pass code review using the local coder model.

    Catches obvious bugs, style issues, and risky patterns. Use as a cheap
    pre-filter before asking the cloud model for a deeper review.

    Args:
        diff_or_code: A unified diff or a code block to review.
    """
    return _client.generate(diff_or_code, system=prompts.CODE_REVIEW, model=model)


@mcp.tool()
def draft_commit_message_local(diff: str, model: str | None = None) -> str:
    """Draft a conventional-style commit message from a diff using the local model.

    Cheap and fast — good for routine commits where the cloud model's
    analysis isn't needed.

    Args:
        diff: The output of ``git diff --staged`` or similar.
    """
    return _client.generate(diff, system=prompts.COMMIT_MESSAGE, model=model)


@mcp.tool()
def extract_local(text: str, what_to_extract: str, model: str | None = None) -> str:
    """Extract specific information from a text block using the local model.

    Good for pulling structured data out of unstructured text — function
    names, URLs, error messages, TODO comments, etc.

    Args:
        text: The source text.
        what_to_extract: What to pull out, e.g. "all function definitions"
            or "every URL in the file".
    """
    return _client.generate(
        prompts.extract_prompt(text, what_to_extract), system=prompts.EXTRACT, model=model
    )


# ---------------------------------------------------------------------------
# Introspection
# ---------------------------------------------------------------------------


@mcp.tool()
def list_models() -> list[str]:
    """List the Ollama models available locally."""
    return _client.list_models()


@mcp.tool()
def server_info() -> dict:
    """Return the server's effective configuration (model, context size, etc.)."""
    return _client.config.as_dict()


def main() -> None:
    """Console-script entry point: run the server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
