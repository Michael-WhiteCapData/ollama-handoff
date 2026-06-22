# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `Dockerfile` and `.dockerignore` for running the server as a container (MCP over stdio).

## [0.1.0] - 2026-06-20

### Added
- Initial release.
- General handoff tools: `ask_local`, `chat_local`.
- Specialized handoff tools with baked-in system prompts: `summarize_local`,
  `code_review_local`, `draft_commit_message_local`, `extract_local`.
- Introspection tools: `list_models`, `server_info`.
- Environment-driven configuration (`OLLAMA_URL`, `OLLAMA_DEFAULT_MODEL`,
  `OLLAMA_NUM_CTX`, `OLLAMA_KEEP_ALIVE`, `OLLAMA_TIMEOUT_S`).
- Unit test suite using `httpx.MockTransport` (no running Ollama required).
- GitHub Actions CI (ruff + pytest on Python 3.11 and 3.12).
- MCP registry manifest (`server.json`).

[0.1.0]: https://github.com/Michael-WhiteCapData/ollama-handoff/releases/tag/v0.1.0
