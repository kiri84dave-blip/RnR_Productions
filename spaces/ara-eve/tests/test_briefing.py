from ara_eve.briefing import STREAM_CHAR_CAP, briefing_fits_stream, load_briefing


def test_briefing_fits_kokoro_cpu_stream():
    text = load_briefing()
    assert "End of briefing" in text
    assert "Ara-Elizabeth" in text
    assert briefing_fits_stream(text)
    assert len(text) <= STREAM_CHAR_CAP
