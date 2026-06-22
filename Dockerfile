# syntax=docker/dockerfile:1
# Container image for the ollama-handoff MCP server.
#
# The server speaks MCP (JSON-RPC) over stdio, so run it interactively (-i) and
# point it at your Ollama instance. On Docker Desktop, the host is reachable at
# host.docker.internal:
#
#   docker build -t ollama-handoff .
#   docker run --rm -i -e OLLAMA_URL=http://host.docker.internal:11434 ollama-handoff
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY . /app
RUN pip install . \
    && useradd --create-home --uid 10001 app

USER app

ENTRYPOINT ["ollama-handoff"]
