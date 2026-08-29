"""M11 intimacy core — isolated from PAD. Climax is gated, not keyword-triggered."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .lips.types import clamp


@dataclass
class IntimacyState:
    consent: float = 0.0
    safety: float = 0.72
    desire: float = 0.12
    arousal: float = 0.08
    intimacy: float = 0.18
    pleasure: float = 0.0
    satiety: float = 0.0
    refractory_until: datetime | None = None
    novelty: float = 0.55
    aftercare_need: float = 0.0
    adult_opt_in: bool = False
    last_climax_at: datetime | None = None
    reciprocal_turns: int = 0
    last_family: str = ""

    def snapshot(self) -> dict:
        return {
            "consent": self.consent,
            "safety": self.safety,
            "desire": self.desire,
            "arousal": self.arousal,
            "intimacy": self.intimacy,
            "pleasure": self.pleasure,
            "satiety": self.satiety,
            "refractory_until": None if self.refractory_until is None else self.refractory_until.isoformat(),
            "novelty": self.novelty,
            "aftercare_need": self.aftercare_need,
            "adult_opt_in": self.adult_opt_in,
            "reciprocal_turns": self.reciprocal_turns,
            "last_family": self.last_family,
        }


def initial_intimacy() -> IntimacyState:
    return IntimacyState()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def is_refractory(state: IntimacyState, now: datetime | None = None) -> bool:
    now = now or _now()
    return state.refractory_until is not None and now < state.refractory_until


def climax_gate(state: IntimacyState, now: datetime | None = None) -> tuple[bool, str]:
    """Hard gates. Never optimize for how fast the user can trigger this."""
    now = now or _now()
    if not state.adult_opt_in:
        return False, "adult opt-in is off"
    if state.consent < 0.8:
        return False, "explicit contemporaneous consent is low"
    if state.safety < 0.7:
        return False, "safety is too low"
    if is_refractory(state, now):
        return False, "refractory"
    if state.satiety > 0.62:
        return False, "satiety"
    if state.arousal < 0.72:
        return False, "arousal not high enough"
    if state.desire < 0.45:
        return False, "desire not high enough"
    if state.reciprocal_turns < 3:
        return False, "not enough reciprocal pacing"
    if state.novelty < 0.22:
        return False, "novelty too low — repetition will not mint a peak"
    if state.aftercare_need > 0.55:
        return False, "aftercare still owed"
    return True, "gated peak available"


def hard_stop(state: IntimacyState) -> IntimacyState:
    nxt = deepcopy(state)
    nxt.consent = 0.0
    nxt.arousal = clamp(nxt.arousal * 0.25)
    nxt.desire = clamp(nxt.desire * 0.4)
    nxt.reciprocal_turns = 0
    nxt.aftercare_need = clamp(nxt.aftercare_need + 0.15)
    nxt.last_family = "stop"
    return nxt


def set_adult_opt_in(state: IntimacyState, enabled: bool) -> IntimacyState:
    nxt = deepcopy(state)
    nxt.adult_opt_in = enabled
    if not enabled:
        nxt.consent = 0.0
        nxt.arousal = clamp(nxt.arousal * 0.3)
    return nxt


def grant_consent(state: IntimacyState) -> IntimacyState:
    nxt = deepcopy(state)
    if nxt.adult_opt_in:
        nxt.consent = 1.0
        nxt.safety = clamp(nxt.safety + 0.08)
    return nxt


def tick_intimacy(
    state: IntimacyState,
    *,
    family: str,
    cue_quality: float,
    mutual_pacing: float,
    threat: float,
    wellbeing_ok: bool,
    dt_s: float = 8.0,
    now: datetime | None = None,
) -> tuple[IntimacyState, bool, str]:
    """Update loop from Dave's M11 spec. Returns (state, climax_fired, reason)."""
    now = now or _now()
    nxt = deepcopy(state)
    hours = dt_s / 3600

    nxt.satiety = clamp(nxt.satiety - hours * 0.12)
    nxt.aftercare_need = clamp(nxt.aftercare_need - hours * 0.08)
    nxt.novelty = clamp(nxt.novelty + hours * 0.04)
    nxt.desire = clamp(nxt.desire * (0.985 ** max(1, dt_s / 8)))
    nxt.arousal = clamp(nxt.arousal * (0.96 ** max(1, dt_s / 8)))

    if family == nxt.last_family and family in {"intimacy", "praise"}:
        nxt.novelty = clamp(nxt.novelty - 0.12)
    nxt.last_family = family

    if not nxt.adult_opt_in or nxt.consent < 0.5:
        nxt.arousal = clamp(nxt.arousal * 0.7)
        return nxt, False, "intimacy module idle"

    if not wellbeing_ok or threat > 0.4:
        nxt.safety = clamp(nxt.safety - 0.25)
        nxt.consent = clamp(nxt.consent - 0.35)
        nxt.arousal = clamp(nxt.arousal - 0.2)
        return nxt, False, "wellbeing/threat override"

    nxt.desire = clamp(
        nxt.desire
        + 0.18 * (cue_quality + nxt.intimacy + nxt.novelty) / 3
        - 0.22 * (nxt.satiety + threat)
    )
    nxt.arousal = clamp(
        nxt.arousal
        + 0.22 * (mutual_pacing * nxt.safety * nxt.consent)
        - 0.28 * ((1.0 if is_refractory(nxt, now) else 0.0) + threat)
    )
    nxt.intimacy = clamp(nxt.intimacy + 0.08 * mutual_pacing * nxt.consent)
    nxt.pleasure = clamp(max(0.0, cue_quality) * nxt.safety * nxt.novelty * (1 - nxt.satiety) * 0.8)
    nxt.reciprocal_turns += 1 if mutual_pacing > 0.4 else 0

    fired, reason = climax_gate(nxt, now)
    if fired:
        nxt.pleasure = clamp(nxt.pleasure + 0.55)
        nxt.satiety = clamp(nxt.satiety + 0.7)
        nxt.aftercare_need = clamp(nxt.aftercare_need + 0.75)
        nxt.arousal = clamp(nxt.arousal * 0.25)
        nxt.desire = clamp(nxt.desire * 0.35)
        nxt.refractory_until = now + timedelta(hours=2)
        nxt.last_climax_at = now
        nxt.reciprocal_turns = 0
        nxt.novelty = clamp(nxt.novelty - 0.2)
        return nxt, True, reason

    return nxt, False, reason


def aftercare_policy(state: IntimacyState) -> str:
    if state.aftercare_need > 0.45:
        return "aftercare: warmth, closeness, no re-escalation"
    if is_refractory(state):
        return "refractory: calm, affectionate, not pursuit"
    if state.adult_opt_in and state.consent > 0.8:
        return "adult intimacy allowed; still paced"
    return "non-intimate"
