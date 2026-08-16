"""MCP server definition: wraps the tool functions in an MCPServer.

Run it over stdio (the default MCP transport) with::

    python -m mcp_server.server

or via the console script ``rnr-mcp-server`` once the package is installed.
"""

from __future__ import annotations

from typing import Any

from mcp.server import MCPServer

from . import __version__, tools

INSTRUCTIONS = (
    "RnR Productions server feeder. Exposes tools to inspect and operate the "
    "host machine: run shell commands, read/write files, list directories, "
    "look up executables, and report system info."
)


def build_server() -> MCPServer:
    """Create and configure the MCP server with all tools registered."""
    server = MCPServer(name="rnr-server-feeder", version=__version__, instructions=INSTRUCTIONS)

    @server.tool(description="Return basic information about the host machine.")
    def system_info() -> dict[str, Any]:
        return tools.system_info()

    @server.tool(description="Run a shell command and capture stdout, stderr, and exit code.")
    def run_command(command: str, timeout: int = 30, cwd: str | None = None) -> dict[str, Any]:
        return tools.run_command(command, timeout=timeout, cwd=cwd)

    @server.tool(description="Read a UTF-8 text file (truncated for safety).")
    def read_text_file(path: str, max_bytes: int = tools.MAX_READ_BYTES) -> dict[str, Any]:
        return tools.read_text_file(path, max_bytes=max_bytes)

    @server.tool(description="Write or append UTF-8 text to a file, creating parent dirs.")
    def write_text_file(path: str, content: str, append: bool = False) -> dict[str, Any]:
        return tools.write_text_file(path, content, append=append)

    @server.tool(description="List the entries of a directory.")
    def list_directory(path: str = ".") -> dict[str, Any]:
        return tools.list_directory(path)

    @server.tool(description="Check whether an executable is available on PATH.")
    def which(program: str) -> dict[str, Any]:
        return tools.which(program)

    return server


def main() -> None:
    """Entry point: run the server over stdio."""
    build_server().run("stdio")


if __name__ == "__main__":
    main()
