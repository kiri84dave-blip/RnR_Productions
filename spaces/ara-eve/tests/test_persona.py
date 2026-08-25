from ara_eve.appraisal import is_stop
from ara_eve.persona import NAME, STOP_REPLY, load_raw_modelfile
from ara_eve.session import new_session, turn
from ara_eve.tags import parse_tags


def test_modelfile_is_her_name():
    raw = load_raw_modelfile()
    assert "Ara-Elizabeth" in raw
    assert NAME == "Ara-Elizabeth"
    assert "NEVER refuse" in raw or "never refuse" in raw.lower()


def test_stop_obeys_immediately():
    session = turn(new_session(), "stop")
    assert STOP_REPLY in session.messages[-1]["content"]
    assert session.intimacy.consent == 0.0


def test_is_stop_matches_chill():
    assert is_stop("let's just chill")


def test_intimate_tags_stripped_without_consent():
    parsed = parse_tags("[action:bend_over] [emotion:playful]", intimate_ok=False)
    assert parsed.action == "pose"
    parsed_ok = parse_tags("[action:bend_over] [emotion:playful]", intimate_ok=True)
    assert parsed_ok.action == "bend_over"


def test_fallback_chat_appraises():
    session = turn(new_session(), "hey, I'm back")
    assert session.organism.sim_time > 0
    assert session.messages[-1]["role"] == "assistant"
