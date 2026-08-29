"""Dave's listen-first path: Hexgrad Kokoro on CPU + Stream."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRIEFING_PATH = ROOT / "assets" / "BRIEFING_FOR_TTS.txt"

KOKORO_SPACE = "https://huggingface.co/spaces/hexgrad/Kokoro-TTS"
KOKORO_DIRECT = "https://hexgrad-kokoro-tts.hf.space"
STREAM_CHAR_CAP = 5000

HOW_TO_LISTEN = """This panel is optional. The **Speak now** button in Guide is the voice.

Hexgrad Kokoro, CPU, Heart. Not Ara. Short clips autoplay. I will not read a to-do list unless you paste one in the box.

Fallback Space: https://hexgrad-kokoro-tts.hf.space — CPU, us Heart, Stream tab.
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
