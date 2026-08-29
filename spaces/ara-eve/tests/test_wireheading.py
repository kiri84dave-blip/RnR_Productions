"""C1: no public path lets the LLM or UI write pleasure directly."""

import inspect

import ara_eve.session as session_mod
from ara_eve.lips.engine import tick
from ara_eve.lips.types import initial_state


def test_tick_requires_appraisal_not_raw_pleasure():
    sig = inspect.signature(tick)
    assert "appraisal" in sig.parameters
    assert "pleasure" not in sig.parameters


def test_session_turn_has_no_pleasure_argument():
    sig = inspect.signature(session_mod.turn)
    assert "pleasure" not in sig.parameters
    assert "liking" not in sig.parameters


def test_cannot_inject_pad_through_new_session():
    s = initial_state()
    assert s.pad.p == 0.12
    s.pad.p = 0.99
    # Direct mutation exists in-process (tests), but no API accepts it from chat.
    assert "pad" not in inspect.signature(session_mod.turn).parameters
