from pathlib import Path

from ara_eve.agent_voice import (
    BUILDER_PREAMBLE,
    GENERATE_CHAR_CAP,
    IDENTITY_SCRIPT,
    STREAM_CHAR_CAP,
    USE_GPU,
    VOICE,
    chunk_for_generate,
    compose_builder_script,
    concat_wavs,
)
from ara_eve.briefing import load_briefing


def test_builder_script_is_not_ara():
    script = compose_builder_script(load_briefing())
    head = script[:220].lower()
    assert "cloud agent" in head
    assert "not ara" in head
    assert "not eve" in head
    assert script.startswith(BUILDER_PREAMBLE)
    assert "End of briefing" in script


def test_generate_chunks_fit_hexgrad_cap():
    script = compose_builder_script(load_briefing())
    chunks = chunk_for_generate(script)
    assert chunks
    assert all(1 <= len(c) <= GENERATE_CHAR_CAP for c in chunks)
    assert " ".join(chunks).split() == script.split()


def test_identity_fits_one_generate_call():
    assert "not Ara-Elizabeth" in IDENTITY_SCRIPT
    assert "not Eve" in IDENTITY_SCRIPT
    assert len(IDENTITY_SCRIPT) <= GENERATE_CHAR_CAP


def test_cpu_heart_not_zerogpu():
    assert USE_GPU is False
    assert VOICE == "af_heart"
    assert STREAM_CHAR_CAP == 5000
    assert GENERATE_CHAR_CAP == 500


def test_identity_file_matches_script():
    text = Path("assets/IDENTITY_FOR_TTS.txt").read_text(encoding="utf-8").strip()
    assert text == IDENTITY_SCRIPT


def test_concat_wavs_preserves_frames(tmp_path):
    import wave

    def write_tone(path: Path, nframes: int) -> None:
        with wave.open(str(path), "wb") as handle:
            handle.setnchannels(1)
            handle.setsampwidth(2)
            handle.setframerate(24000)
            handle.writeframes(b"\x01\x00" * nframes)

    a = tmp_path / "a.wav"
    b = tmp_path / "b.wav"
    out = tmp_path / "out.wav"
    write_tone(a, 100)
    write_tone(b, 50)
    concat_wavs([a, b], out, gap_seconds=0)
    with wave.open(str(out), "rb") as handle:
        assert handle.getnframes() == 150
        assert handle.getframerate() == 24000


def test_app_keeps_builder_off_aras_speak():
    src = Path("app.py").read_text(encoding="utf-8")
    assert "do_builder_speak" in src
    assert 'speak_btn.click(do_speak' in src
    assert "builder_brief_btn.click(do_builder_speak" in src
    assert "help_speak_btn.click(do_help_speak" in src
    assert "Ara speaks last reply" in src
    assert "Speak identity (builder, short)" in src
    assert "Read this topic aloud (builder)" in src
