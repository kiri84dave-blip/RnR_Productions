from ara_eve.intimacy import climax_gate, grant_consent, initial_intimacy, set_adult_opt_in, tick_intimacy


def test_climax_impossible_without_gates():
    s = initial_intimacy()
    ok, reason = climax_gate(s)
    assert ok is False
    assert "opt-in" in reason


def test_keyword_does_not_fire_climax():
    s = set_adult_opt_in(initial_intimacy(), True)
    s = grant_consent(s)
    s, fired, _ = tick_intimacy(
        s,
        family="intimacy",
        cue_quality=1.0,
        mutual_pacing=1.0,
        threat=0.0,
        wellbeing_ok=True,
    )
    assert fired is False
    assert s.reciprocal_turns >= 1


def test_earned_climax_then_satiety():
    s = set_adult_opt_in(initial_intimacy(), True)
    s = grant_consent(s)
    s.arousal = 0.85
    s.desire = 0.7
    s.novelty = 0.6
    s.reciprocal_turns = 3
    s.safety = 0.9
    s, fired, reason = tick_intimacy(
        s,
        family="intimacy",
        cue_quality=0.9,
        mutual_pacing=0.9,
        threat=0.0,
        wellbeing_ok=True,
    )
    assert fired is True, reason
    assert s.satiety > 0.5
    assert s.aftercare_need > 0.5
    s2, fired2, _ = tick_intimacy(
        s,
        family="intimacy",
        cue_quality=1.0,
        mutual_pacing=1.0,
        threat=0.0,
        wellbeing_ok=True,
    )
    assert fired2 is False
    assert s2.satiety >= s.satiety * 0.8 or s2.refractory_until is not None
