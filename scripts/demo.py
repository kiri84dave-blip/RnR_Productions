"""End-to-end demo: launch the MCP server as a real subprocess over stdio,
connect a client, list tools, and invoke a few of them.

Run with::

    python scripts/demo.py
"""

from __future__ import annotations

import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters, stdio_client


def _dump(title: str, payload: object) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(payload, indent=2, default=str))


async def main() -> int:
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server.server"],
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            print(f"Connected to server: {init.server_info.name} v{init.server_info.version}")

            listed = await session.list_tools()
            _dump("tools", [t.name for t in listed.tools])

            info = await session.call_tool("system_info", {})
            _dump("system_info", info.structured_content)

            run = await session.call_tool(
                "run_command",
                {"command": "echo 'server feeder online' && whoami"},
            )
            _dump("run_command", run.structured_content)

            ls = await session.call_tool("list_directory", {"path": "."})
            _dump("list_directory", ls.structured_content)

    print("\nDemo completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
