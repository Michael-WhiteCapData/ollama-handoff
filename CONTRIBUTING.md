# Contributing to ollama-handoff

Thanks for your interest! This project stays intentionally small and focused, so contributions that keep it that way are the easiest to merge.

## Getting set up

```bash
git clone https://github.com/Michael-WhiteCapData/ollama-handoff
cd ollama-handoff
uv pip install -e ".[dev]"
```

## Before opening a PR

- `ruff check .` passes (run `ruff check --fix .` to autofix).
- `pytest` passes. Tests use `httpx.MockTransport`, so **you do not need a running Ollama** to run them.
- New behavior comes with a test.
- Public functions keep their type annotations and a short docstring.

## Adding a new handoff tool

The sweet spot for this project is **specialized handoff tools** — a tool with a baked-in system prompt that an agent will reach for automatically. To add one:

1. Add the system prompt (and any prompt-builder) to `src/ollama_handoff/prompts.py`.
2. Add the `@mcp.tool()` function in `src/ollama_handoff/server.py`. Write the docstring **for the calling agent**: say *when* to use this tool over `ask_local`.
3. Add a test in `tests/test_server_tools.py` asserting the right system prompt is sent.
4. Add a row to the tool table in `README.md`.

## Reporting bugs

Open an issue with: what you ran, what you expected, what happened, and your `server_info` output if relevant.

## Code of conduct

Be decent. Assume good faith. Keep it constructive.
