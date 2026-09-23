<!-- mcp-name: io.github.Michael-WhiteCapData/ollama-handoff -->

# Ollama Handoff

**Local summaries, extractions, code reviews, and commit drafts for your MCP client.**

[![CI](https://github.com/Michael-WhiteCapData/ollama-handoff/actions/workflows/ci.yml/badge.svg)](https://github.com/Michael-WhiteCapData/ollama-handoff/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/ollama-handoff?color=3775A9&logo=pypi&logoColor=white)](https://pypi.org/project/ollama-handoff/)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-server-D97757)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Ollama Handoff lets your agent send routine text tasks to a model running on your machine. Eight MCP tools provide focused prompts, model discovery, and configuration checks.

Local inference does not incur cloud model API charges. Your calling agent can still use paid tokens to plan tasks and read results. Speed, memory use, and quality depend on your model and hardware.

## Quick start

### 1. Prepare Ollama

Install [Ollama](https://ollama.com/download) and [uv](https://docs.astral.sh/uv/getting-started/installation/). Python 3.11 or newer is required; uv can manage Python for you.

```sh
ollama pull llama3.1:8b
ollama list
```

Keep Ollama running. If the desktop app or service is not already running, start `ollama serve` in another terminal.

These examples select `llama3.1:8b`. You can substitute another installed model. Without an override, the package defaults to `qwen2.5-coder:14b`, which must be downloaded separately.

### 2. Register the server

For Claude Code:

```sh
claude mcp add --transport stdio --env OLLAMA_DEFAULT_MODEL=llama3.1:8b ollama-handoff -- uvx ollama-handoff@0.1.3
```

For a client that accepts an `mcpServers` JSON configuration:

```json
{
  "mcpServers": {
    "ollama-handoff": {
      "command": "uvx",
      "args": ["ollama-handoff@0.1.3"],
      "env": {
        "OLLAMA_DEFAULT_MODEL": "llama3.1:8b"
      }
    }
  }
}
```

Add this entry using your client's MCP settings, then reconnect or restart it. If the client cannot find `uvx`, use the absolute path reported by `where.exe uvx` on Windows or `command -v uvx` on macOS and Linux.

Version 0.1.3 declares the MCP compatibility constraint automatically. This server uses the MCP 1 `FastMCP` API, which MCP 2 removed. If you remain on version 0.1.2, add `--with "mcp<2"` to the uvx command.

For pip, install into a virtual environment and configure your client to run that environment's `ollama-handoff` executable:

```sh
python -m pip install "ollama-handoff==0.1.3"
```

### 3. Verify the connection

Ask your agent:

> Call `server_info` and `list_models` from Ollama Handoff. Confirm that the configured model is installed. Then call `summarize_local` with the following text, focusing on the failed test:
>
> ```text
> 10:00:01 INFO Starting build
> 10:00:02 INFO Compiled 12 modules
> 10:00:03 ERROR tests/test_checkout.py::test_total expected 42.00, got 40.00
> 10:00:03 ERROR Build stopped because one test failed
> ```

Check that the summary identifies `test_total`, the expected total of `42.00`, and the actual total of `40.00`. Wording varies by model. Tools accept text, not file paths: your agent must supply file contents when needed.

## Run the demo without an agent

The [demo](examples/demo.py) launches the real MCP server over stdio, discovers its tools, checks configuration, lists installed models, and summarizes the synthetic log above. It requires local Ollama but no cloud API key.

```sh
git clone https://github.com/Michael-WhiteCapData/ollama-handoff.git
cd ollama-handoff
uv venv
uv pip install -e .
uv run --no-project python examples/demo.py --model llama3.1:8b
```

A successful run discovers **8 tools**, lists your model, and returns the summary. Each call prints its elapsed time. Verified on Windows with Python 3.14, MCP 1.30.0, and `llama3.1:8b`. Timing is not a benchmark; the first model load may take longer.

## Tools

| Tool | Use it for |
| --- | --- |
| `ask_local` | A single prompt with an optional system instruction |
| `chat_local` | A conversation with explicit message history |
| `summarize_local` | Summaries of supplied text, optionally focused on a topic |
| `code_review_local` | Initial review of supplied code or a diff |
| `draft_commit_message_local` | A commit message from a supplied diff |
| `extract_local` | Extracting items such as URLs, names, or error codes |
| `list_models` | Discovering installed Ollama models |
| `server_info` | Inspecting effective server configuration |

Generated summaries and reviews need checking. The server does not read files, stage changes, or create commits for you.

## Configuration

Set these variables in your MCP registration:

| Variable | Default | Description |
| --- | --- | --- |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_DEFAULT_MODEL` | `qwen2.5-coder:14b` | Model used when a tool call omits a model |
| `OLLAMA_NUM_CTX` | `32768` | Context window in tokens |
| `OLLAMA_KEEP_ALIVE` | `30m` | Time to keep the model loaded |
| `OLLAMA_TIMEOUT_S` | `600` | Generation and chat request timeout in seconds |

For a small task on a machine with limited memory, try `OLLAMA_NUM_CTX=4096` and a smaller model.

The selected Ollama endpoint receives the text sent to these tools. A remote endpoint sends that text to another machine. Local execution does not prevent your calling client from sending prompts or results to its own cloud provider.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| `No module named mcp.server.fastmcp` | Upgrade to version 0.1.3 and restart the MCP client |
| `uvx` not found | Restart the client after installing uv, or configure the absolute executable path |
| Connection refused | Confirm Ollama is running and `OLLAMA_URL` points to it |
| Model not found | Match the full name from `ollama list`, or download the model with `ollama pull` |
| Slow response or timeout | Allow for model loading; try a smaller model or context |
| Server appears idle in a terminal | This stdio server waits for an MCP client; it is not an interactive chat CLI |

`server_info` checks configuration without contacting Ollama. `list_models` checks connectivity. A successful `summarize_local` call also confirms generation.

## Docker

The included Dockerfile builds the source package. Keep stdin open for MCP:

```sh
docker build -t ollama-handoff .
docker run --rm -i -e OLLAMA_URL=http://host.docker.internal:11434 -e OLLAMA_DEFAULT_MODEL=llama3.1:8b ollama-handoff
```

On Linux without Docker Desktop, use `--network=host` with `OLLAMA_URL=http://localhost:11434`. Do not add `-t` when an MCP client launches the container.

## Development

```sh
uv venv
uv pip install -e ".[dev]"
uv run --no-project ruff check .
uv run --no-project pytest
```

Unit tests use `httpx.MockTransport` and do not need Ollama. The demo uses real inference. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE) Â© Michael Tierney
