# RnR_Productions

An MCP "server feeder" — a [Model Context Protocol](https://modelcontextprotocol.io)
server that exposes a controlled set of tools an AI agent can use to inspect and
operate the machine it runs on (and, in the future, remote server machines it is
pointed at).

This is the foundation for connecting an agent to real compute: it starts on the
local host and is designed to grow into a bridge to a dedicated server box.

## Tools exposed

| Tool | What it does |
| --- | --- |
| `system_info` | Basic facts about the host (OS, CPU, cwd, user). |
| `run_command` | Run a shell command; returns stdout, stderr, exit code (with timeout). |
| `read_text_file` | Read a UTF-8 text file (truncated for safety). |
| `write_text_file` | Write or append UTF-8 text to a file. |
| `list_directory` | List a directory's entries. |
| `which` | Check whether an executable is on `PATH`. |

## Setup

```bash
python3 -m venv .venv
./.venv/bin/pip install -e '.[dev]'
```

## Run the server

The server speaks MCP over stdio (the standard transport):

```bash
./.venv/bin/rnr-mcp-server
# or
./.venv/bin/python -m mcp_server.server
```

Point an MCP client (e.g. Cursor, Claude Desktop, or the demo below) at that
command to use the tools.

## Try it end to end

Launches the server as a subprocess, connects a client, lists tools, and calls
a few of them:

```bash
./.venv/bin/python scripts/demo.py
```

## Develop

```bash
./.venv/bin/ruff check .      # lint
./.venv/bin/python -m pytest  # tests
```

## Layout

- `mcp_server/tools.py` — pure tool implementations (unit-tested directly).
- `mcp_server/server.py` — MCP server that registers the tools.
- `scripts/demo.py` — end-to-end stdio demo/client.
- `tests/` — unit tests plus an in-memory MCP protocol test.
