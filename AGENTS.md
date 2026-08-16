# AGENTS.md

## Project

RnR Productions MCP "server feeder": a Model Context Protocol (MCP) server that
exposes tools for an agent to operate a host machine (run commands, read/write
files, list directories, system info) and is intended to grow into a bridge to a
remote server box. Written in Python using the official `mcp` SDK (v2.x).

Standard commands live in `README.md` and `pyproject.toml`. Key ones:
- Lint: `./.venv/bin/ruff check .`
- Test: `./.venv/bin/python -m pytest`
- Run server (stdio): `./.venv/bin/rnr-mcp-server` (or `python -m mcp_server.server`)
- End-to-end demo: `./.venv/bin/python scripts/demo.py`

## Cursor Cloud specific instructions

- Dependencies are installed into a project-local virtualenv at `.venv` by the
  environment `install` step (`pip install -e '.[dev]'`). Always call tools via
  `./.venv/bin/...` (e.g. `./.venv/bin/python`, `./.venv/bin/pytest`,
  `./.venv/bin/ruff`); the system `python3` does not have the deps.
- The MCP server communicates over **stdio**, not a TCP port. Running
  `rnr-mcp-server` directly will appear to "hang" — that is correct; it is
  waiting for an MCP client on stdin/stdout. Do not treat that as a failure. To
  exercise it non-interactively, run `scripts/demo.py`, which spawns the server
  as a subprocess and drives it over the protocol.
- This repo uses the `mcp` SDK **v2.x**, whose API differs from older FastMCP
  examples: the high-level server class is `mcp.server.MCPServer` (not
  `FastMCP`), and result/model fields are snake_case (e.g.
  `InitializeResult.server_info`, `CallToolResult.structured_content`). Use a
  high-level in-memory `mcp.Client(server)` for protocol tests and
  `stdio_client` + `ClientSession` for real subprocess connections.
- Tool logic is kept in `mcp_server/tools.py` as plain functions so it can be
  unit-tested without a protocol session; `mcp_server/server.py` only wraps them.
