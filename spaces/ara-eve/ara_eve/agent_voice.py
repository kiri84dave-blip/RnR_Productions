"""Builder voice through Hexgrad Kokoro — not Ara, not Eve.

Hexgrad closes the official Gradio API on that Space. The browser queue still
works: CPU is `use_gpu=False`, Heart is `af_heart`, Generate is fn_index 4
(500 chars, returns a wav), Stream is fn_index 6 (5000 chars, HLS).

Ara's Speak button stays on local Kokoro in tts.py. This module is only for
the agent talking to Dave.
"""

from __future__ import annotations

import json
import secrets
import tempfile
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

KOKORO_DIRECT = "https://hexgrad-kokoro-tts.hf.space"
KOKORO_SPACE = "https://huggingface.co/spaces/hexgrad/Kokoro-TTS"
VOICE = "af_heart"
USE_GPU = False  # CPU. Dave's path. Do not flip this to ZeroGPU.
SPEED = 1
GENERATE_FN = 4
STREAM_FN = 6
GENERATE_CHAR_CAP = 500
STREAM_CHAR_CAP = 5000
JOIN_TIMEOUT = 60
SSE_TIMEOUT = 180

BUILDER_PREAMBLE = (
    "Hey Dave. This is the cloud agent talking through Hexgrad Kokoro on CPU. "
    "Not Ara. Not Eve. This briefing is mine."
)

IDENTITY_SCRIPT = (
    "Hey Dave. This is the cloud agent talking, not Ara-Elizabeth, not Eve. "
    "I hooked my own text into Hexgrad Kokoro on CPU, Heart voice, Stream and "
    "Generate, the same Space you already use. Ara's Speak button is still hers. "
    "This clip is mine."
)

_UA = "Mozilla/5.0 AraEve-builder-voice/1.0"


def compose_builder_script(body: str) -> str:
    text = (body or "").strip()
    if not text:
        return BUILDER_PREAMBLE
    if text.startswith(BUILDER_PREAMBLE) or text.lower().startswith("hey dave. this is the cloud agent"):
        return text
    return f"{BUILDER_PREAMBLE}\n\n{text}"


def chunk_for_generate(text: str, cap: int = GENERATE_CHAR_CAP) -> list[str]:
    """Split under Hexgrad Generate's 500-character cap, preferring sentences."""
    body = (text or "").strip()
    if not body:
        return []
    if cap < 32:
        raise ValueError("generate cap is too small")
    chunks: list[str] = []
    remaining = body
    while remaining:
        if len(remaining) <= cap:
            chunks.append(remaining)
            break
        window = remaining[:cap]
        cut = -1
        for sep in ("\n\n", ". ", "? ", "! ", "; ", ", ", "\n", " "):
            idx = window.rfind(sep)
            if idx >= max(24, cap // 5):
                cut = idx + len(sep)
                break
        if cut < 0:
            cut = cap
        piece = remaining[:cut].strip()
        if not piece:
            piece = remaining[:cap].strip()
            cut = cap
        chunks.append(piece)
        remaining = remaining[cut:].lstrip()
    return chunks


def _join(fn_index: int, text: str, session_hash: str) -> dict:
    payload = {
        "data": [text, VOICE, SPEED, USE_GPU],
        "event_data": None,
        "fn_index": fn_index,
        "trigger_id": 19,
        "session_hash": session_hash,
    }
    req = urllib.request.Request(
        f"{KOKORO_DIRECT}/gradio_api/queue/join",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": _UA},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=JOIN_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def _sse_until_done(session_hash: str) -> dict:
    req = urllib.request.Request(
        f"{KOKORO_DIRECT}/gradio_api/queue/data?session_hash={session_hash}",
        headers={"Accept": "text/event-stream", "User-Agent": _UA},
    )
    last: dict = {}
    with urllib.request.urlopen(req, timeout=SSE_TIMEOUT) as response:
        buf = b""
        deadline = time.time() + SSE_TIMEOUT
        while time.time() < deadline:
            chunk = response.read(4096)
            if not chunk:
                break
            buf += chunk
            while b"\n\n" in buf:
                raw, buf = buf.split(b"\n\n", 1)
                line = raw.decode("utf-8", "replace")
                data_lines = [
                    part[6:]
                    for part in line.split("\n")
                    if part.startswith("data: ")
                ]
                if not data_lines:
                    continue
                event = json.loads("\n".join(data_lines))
                msg = event.get("msg")
                if msg == "heartbeat":
                    continue
                if msg in {"process_generating", "process_completed"}:
                    last = event
                if msg == "process_completed":
                    return last
                if msg == "close_stream":
                    return last
    if not last:
        raise RuntimeError("Hexgrad Kokoro queue produced no audio")
    return last


def _file_url(event: dict) -> str:
    output = event.get("output") or {}
    if output.get("error"):
        raise RuntimeError(f"Hexgrad Kokoro error: {output['error']}")
    data = output.get("data") or []
    if not data:
        raise RuntimeError("Hexgrad Kokoro returned empty audio")
    item = data[0]
    if isinstance(item, str) and item.startswith("http"):
        return item
    if isinstance(item, dict):
        url = item.get("url") or ""
        if url:
            return url
        path = item.get("path") or ""
        if path:
            return f"{KOKORO_DIRECT}/gradio_api/file={path}"
    raise RuntimeError(f"Hexgrad Kokoro audio payload not understood: {item!r}")


def _download(url: str, dest: Path) -> Path:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=JOIN_TIMEOUT) as response:
        dest.write_bytes(response.read())
    if dest.stat().st_size < 64:
        raise RuntimeError("Hexgrad Kokoro download was empty")
    return dest


def generate_wav_chunk(text: str, dest: Path) -> Path:
    body = text.strip()
    if len(body) > GENERATE_CHAR_CAP:
        raise ValueError(f"Generate chunk is {len(body)} chars; cap is {GENERATE_CHAR_CAP}")
    session_hash = secrets.token_hex(6)
    _join(GENERATE_FN, body, session_hash)
    event = _sse_until_done(session_hash)
    return _download(_file_url(event), dest)


def stream_playlist_url(text: str) -> str:
    body = text.strip()
    if len(body) > STREAM_CHAR_CAP:
        raise ValueError(f"Stream script is {len(body)} chars; cap is {STREAM_CHAR_CAP}")
    session_hash = secrets.token_hex(6)
    _join(STREAM_FN, body, session_hash)
    event = _sse_until_done(session_hash)
    return _file_url(event)


def _wav_params(path: Path) -> tuple[int, int, int]:
    with wave.open(str(path), "rb") as handle:
        return handle.getnchannels(), handle.getsampwidth(), handle.getframerate()


def _silence_frames(nchannels: int, sampwidth: int, framerate: int, seconds: float) -> bytes:
    nframes = int(framerate * seconds)
    return b"\x00" * (nframes * nchannels * sampwidth)


def concat_wavs(paths: list[Path], dest: Path, gap_seconds: float = 0.25) -> Path:
    if not paths:
        raise ValueError("no wavs to concatenate")
    nchannels, sampwidth, framerate = _wav_params(paths[0])
    with wave.open(str(dest), "wb") as out:
        out.setnchannels(nchannels)
        out.setsampwidth(sampwidth)
        out.setframerate(framerate)
        gap = _silence_frames(nchannels, sampwidth, framerate, gap_seconds)
        for index, path in enumerate(paths):
            with wave.open(str(path), "rb") as src:
                if (
                    src.getnchannels() != nchannels
                    or src.getsampwidth() != sampwidth
                    or src.getframerate() != framerate
                ):
                    raise RuntimeError(f"wav format mismatch in {path}")
                out.writeframes(src.readframes(src.getnframes()))
            if index < len(paths) - 1 and gap:
                out.writeframes(gap)
    return dest


def speak_builder(text: str, dest: Path | None = None) -> Path:
    """Render builder text on Hexgrad Kokoro CPU Heart. Returns a local wav path."""
    script = compose_builder_script(text)
    chunks = chunk_for_generate(script)
    if not chunks:
        raise ValueError("nothing to speak")
    work = Path(tempfile.mkdtemp(prefix="ara-builder-kokoro-"))
    parts: list[Path] = []
    last_error: Exception | None = None
    for index, chunk in enumerate(chunks):
        part = work / f"part-{index:02d}.wav"
        for attempt in range(3):
            try:
                generate_wav_chunk(chunk, part)
                parts.append(part)
                last_error = None
                break
            except (urllib.error.URLError, TimeoutError, RuntimeError, json.JSONDecodeError) as exc:
                last_error = exc
                time.sleep(1.5 * (attempt + 1))
        if last_error is not None and (not parts or parts[-1] != part):
            raise RuntimeError(f"Hexgrad Kokoro failed on chunk {index + 1}/{len(chunks)}: {last_error}") from last_error
    out = dest or Path(tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name)
    concat_wavs(parts, out)
    return out


def speak_builder_to_temp(text: str) -> str:
    return str(speak_builder(text))
