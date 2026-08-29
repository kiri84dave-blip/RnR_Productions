"""Dave's listen-first path: Hexgrad Kokoro on CPU + Stream."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRIEFING_PATH = ROOT / "assets" / "BRIEFING_FOR_TTS.txt"

KOKORO_SPACE = "https://huggingface.co/spaces/hexgrad/Kokoro-TTS"
KOKORO_DIRECT = "https://hexgrad-kokoro-tts.hf.space"
STREAM_CHAR_CAP = 5000

HOW_TO_LISTEN = """This panel is the builder talking. Not Ara. Not Eve.

The **Speak as builder** button sends this script to Hexgrad Kokoro on CPU, Heart voice — the same Space you already use. Their official API is closed, so we use the browser queue: Generate for wavs (500 characters per shot, stitched), Stream as a fallback in the iframe.

If the button is busy or Hexgrad is queued:

1. Open the direct Kokoro Space (CPU, no ZeroGPU quota).
2. Paste the builder script below into Input Text.
3. Voice: us Heart. Hardware: CPU. Not GPU.
4. Open the Stream tab. Click Stream. The first click sometimes yields no audio — that is their Gradio bug. Click Stream again.

Quick links
- Direct (paste + stream): https://hexgrad-kokoro-tts.hf.space
- Hugging Face page: https://huggingface.co/spaces/hexgrad/Kokoro-TTS
- Builder identity: assets/IDENTITY_FOR_TTS.txt
- Briefing file: assets/BRIEFING_FOR_TTS.txt
"""


def load_briefing() -> str:
    return BRIEFING_PATH.read_text(encoding="utf-8").strip() + "\n"


def briefing_fits_stream(text: str | None = None) -> bool:
    body = load_briefing() if text is None else text
    return 0 < len(body) <= STREAM_CHAR_CAP


KOKORO_EMBED_HTML = f"""
<div class="kokoro-wrap">
  <p class="kokoro-links">
    <a href="{KOKORO_DIRECT}" target="_blank" rel="noopener">Open Kokoro direct (CPU Stream)</a>
    &nbsp;·&nbsp;
    <a href="{KOKORO_SPACE}" target="_blank" rel="noopener">Hugging Face page</a>
  </p>
  <iframe
    src="{KOKORO_DIRECT}"
    title="Hexgrad Kokoro TTS"
    width="100%"
    height="640"
    frameborder="0"
    allow="autoplay"
  ></iframe>
  <script type="module" src="https://gradio.s3-us-west-2.amazonaws.com/5.24.0/gradio.js"></script>
</div>
"""
