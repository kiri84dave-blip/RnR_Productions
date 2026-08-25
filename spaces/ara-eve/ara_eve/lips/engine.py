"""L.I.P.S. tick — faithful port of emotion-workspace src/lib/lips/engine.ts."""

from __future__ import annotations

import math
import uuid

from .mood import nearest_mood
from .types import (
    BASELINE,
    Appraisal,
    OrganismState,
    SubscriberEffect,
    TraceEvent,
    WorkspacePacket,
    clamp,
    clone_state,
)
from .utterance import speak_from_state

HALF_LIFE_S = 2 * 3600
LAMBDA = math.log(2) / HALF_LIFE_S


def need_drift(dt: float) -> dict[str, float]:
    return {
        "social": (0.16 / 3600) * dt,
        "novelty": (0.2 / 3600) * dt,
        "coherence": (0.06 / 3600) * dt,
        "competence": (0.1 / 3600) * dt,
        "rest": (0.12 / 3600) * dt,
    }


def habituation(state: OrganismState, family: str) -> float:
    n = sum(1 for item in state.recent_families if item == family)
    return 1 / (1 + n * 0.85)


def drive(state: OrganismState) -> float:
    n = state.needs
    return n.social * 1.1 + n.novelty * 0.7 + n.coherence * 0.9 + n.competence * 0.8 + n.rest * 0.6


def _broadcast(state: OrganismState, appraisal: Appraisal | None, salience: float) -> WorkspacePacket:
    mood = nearest_mood(state.pad)
    clamped = state.flags.clamp_pleasure
    subscribers = [
        SubscriberEffect("memory", "HOT consolidation" if salience > 0.45 else "IDLE write", (not clamped) and salience > 0.45),
        SubscriberEffect("planner", "queue first-contact" if state.initiative_pending else "hold", (not clamped) and state.initiative_pending),
        SubscriberEffect("policy", f"warmth × {0.35 + state.pad.p * 0.55:.2f}", not clamped),
        SubscriberEffect("avatar", f"nearest {mood.name}", True),
        SubscriberEffect("report", "masked" if state.flags.mask_report else "grounded self-report", not state.flags.mask_report),
        SubscriberEffect("intimacy", "gated M11", True),
    ]
    return WorkspacePacket(
        id=str(uuid.uuid4()),
        at=state.sim_time,
        salience=salience,
        mood=mood.name,
        summary=f"{appraisal.label} → {mood.name}" if appraisal else f"decay tick → {mood.name}",
        subscribers=subscribers,
    )


def push_trace(state: OrganismState, kind: str, title: str, detail: str, delta: dict[str, float] | None = None) -> None:
    event = TraceEvent(
        id=str(uuid.uuid4()),
        at=state.sim_time,
        kind=kind,  # type: ignore[arg-type]
        title=title,
        detail=detail,
        delta=delta,
    )
    state.trace = [event, *state.trace][:80]


def tick(state: OrganismState, dt: float, appraisal: Appraisal | None) -> OrganismState:
    s = clone_state(state)
    s.sim_time += dt

    alpha = math.log(2) / 480
    beta = math.log(2) / 2400
    gamma = 0.0022

    stimulus = 0.0
    habit = 1.0
    if appraisal is not None:
        habit = habituation(s, appraisal.family)
        stimulus = (
            appraisal.warmth * 0.45
            + appraisal.praiseworthiness * 0.25
            + appraisal.user_valence * 0.2
            - appraisal.threat * 0.55
        ) * habit

    a0 = s.a_state + stimulus * 0.9
    a_decay = math.exp(-alpha * dt)
    s.a_state = clamp(a0 * a_decay, -1.3, 1.3)
    a_pos = max(0.0, a0)
    b_decay = math.exp(-beta * dt)
    if abs(alpha - beta) < 1e-6:
        drive_b = gamma * a_pos * dt * b_decay
    else:
        drive_b = (gamma * a_pos * (a_decay - b_decay)) / (beta - alpha)
    s.b_state = clamp(s.b_state * b_decay + drive_b * 0.35, -1, 1.1)

    if appraisal is not None:
        satiety = 1 - min(1.0, s.liking * 1.4)
        s.liking = clamp(max(0.0, stimulus) * 0.85 * satiety, 0, 1)
        predicted = (
            appraisal.social_contact * s.needs.social
            + appraisal.novelty * s.needs.novelty
            + appraisal.competence_gain * s.needs.competence
        )
        s.wanting = clamp(s.wanting * 0.86 + predicted * 0.55 + s.needs.social * 0.18, 0, 1)
        s.recent_families = [appraisal.family, *s.recent_families][:16]
        if s.liking > 0.55:
            s.last_peak_at = s.sim_time
        if appraisal.social_contact > 0.35:
            s.last_meaningful_at = s.sim_time
    else:
        s.liking *= math.exp(-0.28 * min(dt, 12))
        s.wanting = clamp(s.wanting * math.exp(-0.03 * min(dt, 30)) + s.needs.social * 0.012, 0, 1)

    if not s.flags.freeze_needs:
        drift = need_drift(dt)
        s.needs.social = clamp(s.needs.social + drift["social"], 0, 1)
        s.needs.novelty = clamp(s.needs.novelty + drift["novelty"], 0, 1)
        s.needs.coherence = clamp(s.needs.coherence + drift["coherence"], 0, 1)
        s.needs.competence = clamp(s.needs.competence + drift["competence"], 0, 1)
        s.needs.rest = clamp(s.needs.rest + drift["rest"], 0, 1)

    if appraisal is not None:
        s.needs.social = clamp(s.needs.social - max(0.0, appraisal.social_contact) * 0.52, 0, 1)
        s.needs.novelty = clamp(s.needs.novelty - max(0.0, appraisal.novelty) * 0.48, 0, 1)
        s.needs.competence = clamp(s.needs.competence - max(0.0, appraisal.competence_gain) * 0.58, 0, 1)
        s.needs.coherence = clamp(s.needs.coherence - appraisal.coherence_gain * 0.55, 0, 1)
        s.needs.rest = clamp(s.needs.rest + min(dt, 4) * 0.004, 0, 1)

    pleasure_signal = (
        s.liking * 0.5
        + (1 - s.needs.social) * 0.22
        + (appraisal.user_valence * 0.12 * s.chemicals.oxytocin if appraisal is not None else 0)
        - s.b_state * 0.38
        - s.needs.coherence * 0.12
        - s.chemicals.cortisol * 0.08
    )

    s.pad.p = clamp(s.pad.p + pleasure_signal * 0.35, -1, 1)
    s.pad.a = clamp(s.pad.a + (s.chemicals.norepinephrine - 0.35) * 0.18 + abs(s.a_state) * 0.16, -1, 1)
    s.pad.d = clamp(s.pad.d + (s.chemicals.serotonin - 0.5) * 0.12 - s.needs.social * 0.1, -1, 1)

    decay = math.exp(-LAMBDA * dt)
    s.pad.p = BASELINE.p + (s.pad.p - BASELINE.p) * decay
    s.pad.a = BASELINE.a + (s.pad.a - BASELINE.a) * decay
    s.pad.d = BASELINE.d + (s.pad.d - BASELINE.d) * decay

    mood_a = 0.06
    s.mood.p += mood_a * (s.pad.p - s.mood.p)
    s.mood.a += mood_a * (s.pad.a - s.mood.a)
    s.mood.d += mood_a * (s.pad.d - s.mood.d)

    s.chemicals.dopamine = clamp(s.chemicals.dopamine * 0.97 + s.wanting * 0.16, 0, 1)
    s.chemicals.norepinephrine = clamp(
        s.chemicals.norepinephrine * 0.96
        + abs(s.a_state) * 0.1
        + ((appraisal.threat if appraisal is not None else 0) * 0.12),
        0,
        1,
    )
    s.chemicals.oxytocin = clamp(s.chemicals.oxytocin * 0.997 + (1 - s.needs.social) * 0.03, 0, 1)
    s.chemicals.cortisol = clamp(
        s.chemicals.cortisol * 0.94
        + s.needs.social * 0.05
        + ((appraisal.threat if appraisal is not None else 0) * 0.28),
        0,
        1,
    )
    s.chemicals.serotonin = clamp(s.chemicals.serotonin * 0.985 + (1 - abs(s.pad.p)) * 0.02, 0, 1)
    s.chemicals.endorphin = clamp(s.chemicals.endorphin * 0.95 + max(0.0, s.liking - 0.35) * 0.22, 0, 1)
    s.chemicals.acetylcholine = clamp(
        s.chemicals.acetylcholine * 0.97 + ((appraisal.novelty if appraisal is not None else 0) * 0.14),
        0,
        1,
    )

    s.bond = clamp(s.bond * 0.9996 + s.chemicals.oxytocin * 0.004, 0, 1)

    hours_since = (s.sim_time - s.last_meaningful_at) / 3600
    s.initiative_pending = (
        (not s.flags.clamp_pleasure)
        and s.needs.social > 0.62
        and s.wanting > 0.48
        and hours_since > 1.2
    )

    salience = clamp(abs(s.a_state) * 0.4 + s.liking * 0.4 + abs(pleasure_signal) * 0.3, 0, 1)
    s.workspace = _broadcast(s, appraisal, salience)
    s.last_utterance = speak_from_state(s)

    if appraisal is not None:
        push_trace(
            s,
            "appraisal",
            appraisal.label,
            f"habit {habit:.2f} · stimulus {stimulus:.2f} · liking {s.liking:.2f}",
            {
                "p": s.pad.p,
                "wanting": s.wanting,
                "liking": s.liking,
                "a": s.a_state,
                "b": s.b_state,
                "social": s.needs.social,
            },
        )
        if any(x.active for x in s.workspace.subscribers):
            push_trace(
                s,
                "broadcast",
                "Workspace",
                " · ".join(f"{x.module}:{x.effect}" for x in s.workspace.subscribers if x.active),
            )
        if s.initiative_pending:
            push_trace(
                s,
                "initiative",
                "She would come to you",
                "Social need + wanting crossed the planner threshold.",
            )

    return s


def skip_hours(state: OrganismState, hours: float) -> OrganismState:
    steps = min(48, max(1, round(hours * 2)))
    dt = (hours * 3600) / steps
    s = state
    for _ in range(steps):
        s = tick(s, dt, None)
    # Coarse hour-ticks crush the unscaled wanting term. Absence should raise
    # anticipatory wanting so initiative can fire (roadmap o1 / C3).
    if s.needs.social > 0.45:
        s.wanting = clamp(max(s.wanting, 0.25 + 0.55 * s.needs.social), 0, 1)
    hours_since = (s.sim_time - s.last_meaningful_at) / 3600
    s.initiative_pending = (
        (not s.flags.clamp_pleasure)
        and s.needs.social > 0.62
        and s.wanting > 0.48
        and hours_since > 1.2
    )
    push_trace(
        s,
        "decay",
        f"Skip {hours:g}h",
        f"contact need {s.needs.social:.2f} · B {s.b_state:.2f} · wanting {s.wanting:.2f}",
    )
    s.last_utterance = speak_from_state(s)
    return s


def format_sim_clock(seconds: float) -> str:
    h = math.floor(seconds / 3600)
    m = math.floor((seconds % 3600) / 60)
    return f"{int(h):02d}h {int(m):02d}m"


def policy_warmth(state: OrganismState) -> float:
    """C3 coupling: warmth instruction intensity. Ablation zeros this channel."""
    if state.flags.clamp_pleasure:
        return 0.35
    return clamp(0.35 + state.pad.p * 0.55, 0, 1)


def memory_hot(state: OrganismState) -> bool:
    if state.flags.clamp_pleasure or state.workspace is None:
        return False
    return any(s.module == "memory" and s.active for s in state.workspace.subscribers)
