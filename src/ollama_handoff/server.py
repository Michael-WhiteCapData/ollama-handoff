"""The ollama-handoff MCP server.

Registers a small set of MCP tools that hand work off to a local Ollama model.
Tool descriptions are written for the *calling agent*: they say when to pick
each tool, so the agent routes cheap work locally without being told to.
"""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from . import prompts
from .config import Config
from .ollama import OllamaClient

mcp = FastMCP("ollama-handoff")

# A single shared client built from the environment. Swapped out in tests.
_client = OllamaClient(Config.from_env())

_MODEL_DESC = (
    "Ollama model name to run, e.g. 'llama3.1' or 'qwen2.5-coder'. "
    "Omit to use the server's configured default model."
)


def set_client(client: OllamaClient) -> None:
    """Replace the module-level Ollama client (used by tests)."""
    global _client
    _client = client


# ---------------------------------------------------------------------------
# General-purpose handoff
# ---------------------------------------------------------------------------


@mcp.tool()
def ask_local(
    prompt: Annotated[str, Field(description="The task or question to send to the model.")],
    model: Annotated[str | None, Field(description=_MODEL_DESC)] = None,
    system: Annotated[
        str | None,
        Field(description="Optional system prompt to set the model's role or behavior."),
    ] = None,
) -> str:
    """Send a one-shot prompt to a local Ollama model and return its text response.

    Use for any handoff where the cloud model's full reasoning isn't needed:
    drafts, boilerplate, simple extractions, formatting, or quick lookups. Runs
    on the user's own GPU and consumes no cloud-LLM usage. Returns the model's
    raw text completion.
    """
    return _client.generate(prompt, system=system, model=model)


@mcp.tool()
def chat_local(
    messages: Annotated[
        list[dict],
        Field(
            description="Conversation as a list of "
            '{"role": "user"|"assistant"|"system", "content": str} messages, in order.'
        ),
    ],
    model: Annotated[str | None, Field(description=_MODEL_DESC)] = None,
) -> str:
    """Hold a multi-turn chat against a local Ollama model.

    Use instead of `ask_local` when the handoff needs more than one turn of
    context — a running conversation or a system + user + assistant history.
    Runs locally at no cloud cost. Returns the model's next assistant message
    as text.
    """
    return _client.chat(messages, model=model)


# ---------------------------------------------------------------------------
# Specialized handoffs — system prompt baked in so the agent doesn't restate
# it, and the description tells the agent when to prefer this over ask_local.
# ---------------------------------------------------------------------------


@mcp.tool()
def summarize_local(
    text: Annotated[
        str,
        Field(
            description="The content to summarize; may be long (the local context window is configurable)."
        ),
    ],
    focus: Annotated[
        str | None,
        Field(
            description="Optional hint to steer the summary, e.g. "
            "'errors and stack traces' or 'API surface only'."
        ),
    ] = None,
    model: Annotated[str | None, Field(description=_MODEL_DESC)] = None,
) -> str:
    """Summarize a block of text using the local model.

    Use to offload long files, logs, transcripts, or docs the cloud model does
    not need to fully ingest — call this instead of reading a large blob into the
    cloud context. Runs on the user's GPU at no cloud cost. Returns a concise
    prose summary; pass `focus` to bias it toward what matters.
    """
    return _client.generate(prompts.summarize_prompt(text, focus), system=prompts.SUMMARIZE, model=model)


@mcp.tool()
def code_review_local(
    diff_or_code: Annotated[str, Field(description="A unified diff or a code block to review.")],
    model: Annotated[str | None, Field(description=_MODEL_DESC)] = None,
) -> str:
    """Run a quick first-pass code review using the local coder model.

    Use as a cheap pre-filter before asking the cloud model for a deeper review:
    it catches obvious bugs, style issues, and risky patterns. Runs locally at no
    cloud cost. Returns review notes as text.
    """
    return _client.generate(diff_or_code, system=prompts.CODE_REVIEW, model=model)


@mcp.tool()
def draft_commit_message_local(
    diff: Annotated[str, Field(description="A staged diff, e.g. the output of `git diff --staged`.")],
    model: Annotated[str | None, Field(description=_MODEL_DESC)] = None,
) -> str:
    """Draft a conventional-style commit message from a diff using the local model.

    Use for routine commits where the cloud model's analysis isn't needed — it is
    cheap and fast. Runs locally at no cloud cost. Returns a single commit message
    (subject plus optional body) as text.
    """
    return _client.generate(diff, system=prompts.COMMIT_MESSAGE, model=model)


@mcp.tool()
def extract_local(
    text: Annotated[str, Field(description="The source text to extract from.")],
    what_to_extract: Annotated[
        str,
        Field(description="What to pull out, e.g. 'all function definitions' or 'every URL in the file'."),
    ],
    model: Annotated[str | None, Field(description=_MODEL_DESC)] = None,
) -> str:
    """Extract specific information from a text block using the local model.

    Use to pull structured facts out of unstructured text — function names, URLs,
    error codes, TODO comments, dependency names — without spending cloud-model
    tokens. Runs locally at no cloud cost. Returns the extracted items as text,
    shaped by `what_to_extract`.
    """
    return _client.generate(
        prompts.extract_prompt(text, what_to_extract),
        system=prompts.EXTRACT,
        model=model,
    )


# ---------------------------------------------------------------------------
# Introspection
# ---------------------------------------------------------------------------


@mcp.tool()
def list_models() -> list[str]:
    """List the Ollama models installed locally and available to these tools.

    Use to discover valid values for the `model` parameter before pinning a
    specific model. Returns a list of model-name strings.
    """
    return _client.list_models()


@mcp.tool()
def server_info() -> dict:
    """Report the server's effective configuration.

    Returns the default model, Ollama base URL, context size, and request
    timeout. Use to confirm which model the tools will use by default or to
    debug connectivity. Returns a JSON object.
    """
    return _client.config.as_dict()


def main() -> None:
    """Console-script entry point: run the server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
