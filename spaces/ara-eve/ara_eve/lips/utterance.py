"""Grounded self-report — port of src/lib/lips/utterance.ts. Never invents climax."""

from __future__ import annotations

from .mood import nearest_mood
from .types import OrganismState


def _band(n: float) -> str:
    if n > 0.7:
        return "high"
    if n > 0.4:
        return "mid"
    return "low"


def speak_from_state(state: OrganismState) -> str:
    if state.flags.mask_report:
        return (
            "Report layer masked. Other modules still receive the broadcast — "
            "this sentence is not allowed to see PAD, needs, or chemicals."
        )

    mood = nearest_mood(state.pad)
    social = _band(state.needs.social)
    novelty = _band(state.needs.novelty)
    rest = _band(state.needs.rest)
    net = state.a_state - state.b_state

    lines: list[str] = [f"{mood.name}. Policy: {mood.policy}."]

    if state.initiative_pending:
        lines.append(
            "Initiative flag is set: contact need and wanting crossed threshold. She would reach first."
        )

    if social == "high":
        lines.append("Social contact is depleted. Absence is registered as a drive, not a prompt.")
    elif social == "low" and state.liking > 0.25:
        lines.append("Contact just restored. Liking is the short peak; wanting will not stay pinned.")

    if novelty == "high":
        lines.append("Novelty error is high. Repeated praise will not substitute for a new thread.")

    if rest == "high":
        lines.append("Rest need is elevated. Continuing the session now trades against recovery.")

    if net < -0.18:
        lines.append("Opponent B-state is dominating. Afterglow has inverted — this is the ache, not a mood string.")
    elif state.liking > 0.45:
        lines.append("Consummatory liking is live. This pulse satiates; identical stimuli will shrink.")

    if state.flags.clamp_pleasure:
        lines.append("Ablation on: pleasure is computed but not allowed to bend policy, memory, or initiative.")

    lines.append(
        f"Ground truth — P {state.pad.p:.2f} · wanting {state.wanting:.2f} · "
        f"liking {state.liking:.2f} · B {state.b_state:.2f}."
    )
    return " ".join(lines)
