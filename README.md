<!-- mcp-name: io.github.Michael-WhiteCapData/ollama-handoff -->

# ollama-handoff

**An MCP server that offloads cheap work from your cloud LLM agent to a local Ollama model.**

[![CI](https://github.com/Michael-WhiteCapData/ollama-handoff/actions/workflows/ci.yml/badge.svg)](https://github.com/Michael-WhiteCapData/ollama-handoff/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/ollama-handoff?color=3775A9&logo=pypi&logoColor=white)](https://pypi.org/project/ollama-handoff/)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-server-D97757)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Your frontier model (Claude, GPT, etc.) is brilliant and metered. A lot of the work it gets handed — summarizing a log, drafting a commit message, pulling every URL out of a file, a quick first-pass code review — **doesn't need frontier reasoning at all.** `ollama-handoff` exposes your local [Ollama](https://ollama.com/) instance as a handful of purpose-built [MCP](https://modelcontextprotocol.io/) tools, so your agent can route that work to a model on **your own GPU** — at **zero cloud cost** — and spend its (paid) reasoning budget on the things that actually need it.

This isn't a generic "wrap the Ollama API" server. Each tool ships with a **baked-in system prompt** and a **description written for the calling agent**, so the agent knows *when* to hand off and gets a tuned result back without re-stating instructions every call.

---

## Why you'd want this

- 💸 **Spend less.** Routine offloads run locally and bill nothing.
- ⚡ **Keep the big model focused.** Summaries, extractions, and drafts don't eat its context or your budget.
- 🧠 **Tuned, not raw.** `summarize_local`, `code_review_local`, `draft_commit_message_local`, and `extract_local` come with reviewer/summarizer/extractor system prompts already dialed in.
- 🔌 **Drop-in.** One MCP registration; works with Claude Code, Claude Desktop, Cursor, and any MCP client.
- 🪶 **Tiny & auditable.** Two dependencies (`mcp`, `httpx`), fully typed, unit-tested, no telemetry.

## Requirements

- [Ollama](https://ollama.com/) running locally (`ollama serve`) with at least one model pulled, e.g. `ollama pull qwen2.5-coder:14b`.
- Python 3.11+ (or just `uvx`, which manages it for you).

## Install

The fastest path is [`uv`](https://docs.astral.sh/uv/) — no manual venv needed:

```bash
uvx ollama-handoff          # run directly
# or
pip install ollama-handoff  # then run: ollama-handoff
```

### Claude Code

```bash
claude mcp add ollama-handoff -- uvx ollama-handoff
```

### Claude Desktop / Cursor (`mcp` config block)

```jsonc
{
  "mcpServers": {
    "ollama-handoff": {
      "command": "uvx",
      "args": ["ollama-handoff"],
      "env": {
        "OLLAMA_DEFAULT_MODEL": "qwen2.5-coder:14b"
      }
    }
  }
}
```

## Tools

| Tool | What it does | When the agent should reach for it |
| --- | --- | --- |
| `ask_local` | One-shot prompt to the local model | Any handoff that doesn't need frontier reasoning |
| `chat_local` | Multi-turn local chat | Handoffs needing more than one turn of context |
| `summarize_local` | Structured summary (headline + bullets) | Long files, logs, transcripts, docs |
| `code_review_local` | Quick first-pass review of a diff/code | Cheap pre-filter before a deep review |
| `draft_commit_message_local` | Conventional commit message from a diff | Routine commits |
| `extract_local` | Pull structured items from unstructured text | URLs, function names, error codes, TODOs |
| `list_models` | List locally available Ollama models | Discovery / choosing a model |
| `server_info` | Report the effective configuration | Debugging setup |

## Configuration

All configuration is via environment variables set in your MCP registration:

| Variable | Default | Description |
| --- | --- | --- |
| `OLLAMA_URL` | `http://localhost:11434` | Base URL of the Ollama server |
| `OLLAMA_DEFAULT_MODEL` | `qwen2.5-coder:14b` | Default model for handoffs |
| `OLLAMA_NUM_CTX` | `32768` | Context window in tokens |
| `OLLAMA_KEEP_ALIVE` | `30m` | How long to keep the model resident in VRAM |
| `OLLAMA_TIMEOUT_S` | `600` | Per-request timeout, seconds |

## Example

Once registered, you don't call the tools yourself — your agent does. A typical exchange:

> **You:** Summarize the errors in `build.log` and draft a commit for the staged fix.
>
> **Agent:** *(calls `summarize_local(build.log, focus="errors and stack traces")` and `draft_commit_message_local(git diff --staged)` — both run on your GPU, nothing billed)* → returns the summary + commit message.

## Development

```bash
git clone https://github.com/Michael-WhiteCapData/ollama-handoff
cd ollama-handoff
uv pip install -e ".[dev]"
ruff check .
pytest          # tests use httpx.MockTransport — no running Ollama required
```

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions welcome — especially new specialized handoff tools.

## License

[MIT](LICENSE) © Michael Tierney
