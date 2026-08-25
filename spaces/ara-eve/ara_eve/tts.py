"""Kokoro TTS. Optional. GPU path is decorated in app.py so ZeroGPU can pack weights."""

from __future__ import annotations

import os
import tempfile
from functools import lru_cache

VOICES = ("af_heart", "af_bella")
SAMPLE_RATE = 24000


@lru_cache(maxsize=1)
def _pipeline():
    from kokoro import KPipeline

    return KPipeline(lang_code="a")


def available() -> bool:
    if os.environ.get("ARA_EVE_DISABLE_TTS") == "1":
        return False
    try:
        import kokoro  # noqa: F401

        return True
    except Exception:
        return False


def synthesize(text: str, voice: str = "af_heart") -> str | None:
    if not text.strip() or not available():
        return None
    chosen = voice if voice in VOICES else "af_heart"
    pipeline = _pipeline()
    chunks: list = []
    for result in pipeline(text[:800], voice=chosen):
        audio = getattr(result, "audio", None)
        if audio is None and isinstance(result, (tuple, list)) and len(result) >= 3:
            audio = result[2]
        if audio is None:
            continue
        try:
            import numpy as np

            arr = audio.detach().cpu().numpy() if hasattr(audio, "detach") else np.asarray(audio)
        except Exception:
            continue
        chunks.append(arr)
    if not chunks:
        return None
    import numpy as np
    import soundfile as sf

    wav = np.concatenate(chunks)
    handle = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(handle.name, wav, SAMPLE_RATE)
    return handle.name
