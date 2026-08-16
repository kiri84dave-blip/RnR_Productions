"""Core tool implementations for the MCP server feeder.

These are plain, side-effect-honest Python functions so they can be unit-tested
directly and reused by the MCP server layer in ``server.py``. Keeping the logic
here (separate from MCP registration) makes the behaviour easy to test without
spinning up a protocol session.
"""

from __future__ import annotations

import os
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

# Guardrail: cap how much file content we will read/return so a single tool call
# can never try to pull an unbounded amount of data back through the protocol.
MAX_READ_BYTES = 1_000_000


def system_info() -> dict[str, Any]:
    """Return basic facts about the machine the server is running on."""
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "cwd": os.getcwd(),
        "user": os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
        "cpu_count": os.cpu_count(),
    }


def run_command(command: str, timeout: int = 30, cwd: str | None = None) -> dict[str, Any]:
    """Run a shell command and capture its result.

    This is the heart of the "server feeder": it lets an agent actually *do*
    things on the host. It intentionally runs through the shell so ordinary
    commands work as typed. ``timeout`` bounds how long a command may run so a
    hung process cannot block the session forever.
    """
    if not command or not command.strip():
        raise ValueError("command must be a non-empty string")

    try:
        completed = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "exit_code": None,
            "stdout": exc.stdout or "",
            "stderr": (exc.stderr or "") + f"\n[timed out after {timeout}s]",
            "timed_out": True,
        }

    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "timed_out": False,
    }


def read_text_file(path: str, max_bytes: int = MAX_READ_BYTES) -> dict[str, Any]:
    """Read a UTF-8 text file, truncating to ``max_bytes`` for safety."""
    p = Path(path).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"no such file: {path}")
    if not p.is_file():
        raise ValueError(f"not a regular file: {path}")

    data = p.read_bytes()
    truncated = len(data) > max_bytes
    text = data[:max_bytes].decode("utf-8", errors="replace")
    return {
        "path": str(p),
        "size_bytes": len(data),
        "truncated": truncated,
        "content": text,
    }


def write_text_file(path: str, content: str, append: bool = False) -> dict[str, Any]:
    """Write (or append) UTF-8 text to a file, creating parent dirs as needed."""
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with p.open(mode, encoding="utf-8") as fh:
        fh.write(content)
    return {
        "path": str(p),
        "bytes_written": len(content.encode("utf-8")),
        "appended": append,
    }


def list_directory(path: str = ".") -> dict[str, Any]:
    """List the entries of a directory with a little metadata about each."""
    p = Path(path).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"no such directory: {path}")
    if not p.is_dir():
        raise ValueError(f"not a directory: {path}")

    entries = []
    for child in sorted(p.iterdir(), key=lambda c: c.name):
        try:
            size = child.stat().st_size if child.is_file() else None
        except OSError:
            size = None
        entries.append(
            {
                "name": child.name,
                "type": "dir" if child.is_dir() else "file",
                "size_bytes": size,
            }
        )
    return {"path": str(p), "count": len(entries), "entries": entries}


def which(program: str) -> dict[str, Any]:
    """Report whether an executable is available on PATH and where."""
    location = shutil.which(program)
    return {"program": program, "found": location is not None, "path": location}


def python_executable() -> str:
    """Return the interpreter path (useful sanity check for the environment)."""
    return sys.executable
