"""Run a local log summary through the MCP stdio interface."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from time import perf_counter

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ollama_handoff.config import Config

SAMPLE_LOG = """10:00:01 INFO Starting build
10:00:02 INFO Compiled 12 modules
10:00:03 ERROR tests/test_checkout.py::test_total expected 42.00, got 40.00
10:00:03 ERROR Build stopped because one test failed
"""


async def demo(model: str) -> None:
    """Discover the server tools and summarize synthetic build output."""
    env = {
        key: value
        for key, value in os.environ.items()
        if key
        in {
            "OLLAMA_URL",
            "OLLAMA_NUM_CTX",
            "OLLAMA_KEEP_ALIVE",
            "OLLAMA_TIMEOUT_S",
        }
    }
    env["OLLAMA_DEFAULT_MODEL"] = model
    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "ollama_handoff.server"],
        env=env,
    )
    async with stdio_client(server) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
        print(f"Connected. Discovered {len(tools.tools)} tools.", flush=True)
        for name, arguments in [
            ("server_info", {}),
            ("list_models", {}),
            (
                "summarize_local",
                {
                    "text": SAMPLE_LOG,
                    "focus": "Identify the failed test and its expected and actual totals.",
                },
            ),
        ]:
            print(f"\n{name}", flush=True)
            started = perf_counter()
            result = await session.call_tool(name, arguments)
            for content in result.content:
                if content.type == "text":
                    print(content.text, flush=True)
            if result.isError:
                raise RuntimeError(f"{name} failed. Check the Ollama service and model name.")
            print(f"Completed in {perf_counter() - started:.1f}s.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=Config.from_env().default_model)
    asyncio.run(demo(parser.parse_args().model))
