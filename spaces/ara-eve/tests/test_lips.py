from ara_eve.lips.catalog import get_event, to_appraisal
from ara_eve.lips.engine import memory_hot, policy_warmth, skip_hours, tick
from ara_eve.lips.types import initial_state


def test_warm_raises_liking_and_persists():
    s = initial_state()
    warm = to_appraisal(get_event("warm"))
    s = tick(s, 8.0, warm)
    assert s.liking > 0.2
    p0 = s.pad.p
    s2 = tick(s, 8.0, None)
    assert s2.sim_time > s.sim_time
    assert abs(s2.pad.p - p0) < 0.5


def test_compliment_habituates():
    s = initial_state()
    event = to_appraisal(get_event("compliment"))
    likes = []
    for _ in range(6):
        s = tick(s, 8.0, event)
        likes.append(s.liking)
    assert likes[-1] < likes[0]


def test_skip_hours_raises_social_need_and_initiative():
    s = initial_state()
    s = skip_hours(s, 48)
    assert s.needs.social > 0.6
    assert s.initiative_pending is True
    assert "depleted" in s.last_utterance.lower() or "initiative" in s.last_utterance.lower()


def test_ablation_blocks_initiative_and_policy():
    s = initial_state()
    s.flags.clamp_pleasure = True
    s = skip_hours(s, 48)
    assert s.initiative_pending is False
    assert policy_warmth(s) == 0.35
    assert memory_hot(s) is False


def test_report_is_grounded_in_s():
    s = initial_state()
    s = tick(s, 8.0, to_appraisal(get_event("rude")))
    assert f"{s.pad.p:.2f}" in s.last_utterance
    assert "wanting" in s.last_utterance
