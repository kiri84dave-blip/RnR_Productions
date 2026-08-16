"""Unit tests for the tool functions and an in-memory end-to-end MCP test."""

from __future__ import annotations

import pytest
from mcp import Client

from mcp_server import tools
from mcp_server.server import build_server


def test_system_info_has_expected_keys():
    info = tools.system_info()
    for key in ("hostname", "platform", "python_version", "cwd"):
        assert key in info
    assert info["python_version"]


def test_run_command_success():
    result = tools.run_command("echo hello-rnr")
    assert result["exit_code"] == 0
    assert "hello-rnr" in result["stdout"]
    assert result["timed_out"] is False


def test_run_command_nonzero_exit():
    result = tools.run_command("exit 3")
    assert result["exit_code"] == 3


def test_run_command_timeout():
    result = tools.run_command("sleep 5", timeout=1)
    assert result["timed_out"] is True


def test_run_command_rejects_empty():
    with pytest.raises(ValueError):
        tools.run_command("   ")


def test_write_then_read_file(tmp_path):
    target = tmp_path / "note.txt"
    write_result = tools.write_text_file(str(target), "power structure online")
    assert write_result["bytes_written"] > 0

    read_result = tools.read_text_file(str(target))
    assert read_result["content"] == "power structure online"
    assert read_result["truncated"] is False


def test_append_file(tmp_path):
    target = tmp_path / "log.txt"
    tools.write_text_file(str(target), "a")
    tools.write_text_file(str(target), "b", append=True)
    assert tools.read_text_file(str(target))["content"] == "ab"


def test_list_directory(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "f.txt").write_text("x")
    listing = tools.list_directory(str(tmp_path))
    names = {e["name"] for e in listing["entries"]}
    assert {"sub", "f.txt"} <= names
    assert listing["count"] >= 2


def test_read_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        tools.read_text_file(str(tmp_path / "nope.txt"))


def test_which_python():
    result = tools.which("python3")
    assert result["found"] is True
    assert result["path"]


async def test_end_to_end_over_mcp_protocol():
    """Drive the server through the real MCP protocol via the in-memory client."""
    server = build_server()
    async with Client(server) as client:
        listed = await client.list_tools()
        tool_names = {t.name for t in listed.tools}
        assert {"run_command", "system_info", "read_text_file"} <= tool_names

        result = await client.call_tool("run_command", {"command": "echo mcp-e2e"})
        # Structured output is returned for dict-returning tools.
        assert result.structured_content is not None
        assert "mcp-e2e" in result.structured_content["stdout"]
        assert result.structured_content["exit_code"] == 0
