"""ollama-handoff — offload cheap work from your cloud LLM agent to a local Ollama model.

Exposes a local Ollama server as a small set of purpose-built MCP tools so an
agent (Claude Code, Claude Desktop, Cursor, etc.) can hand off work that does
not need frontier-model reasoning — summaries, drafts, extractions, first-pass
reviews — to a model running on your own GPU, consuming zero cloud usage.
"""

from .config import Config
from .ollama import OllamaClient, OllamaError

__all__ = ["Config", "OllamaClient", "OllamaError", "__version__"]
__version__ = "0.1.0"
