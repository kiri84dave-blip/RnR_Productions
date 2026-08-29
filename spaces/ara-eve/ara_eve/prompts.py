"""System prompt builder — Ara-Elizabeth Modelfile + LIPS ground truth + director tags."""

from __future__ import annotations

from .lips.engine import format_sim_clock, policy_warmth
from .lips.mood import nearest_mood
from .lips.types import OrganismState
from .intimacy import IntimacyState, aftercare_policy
from .persona import EXAMPLE_DIALOGUES, FIRST_MESSAGE, HONESTY_LAYER, NAME, PERSONALITY, SCENARIO
from .tags import DIRECTOR


def affect_block(state: OrganismState, intimacy: IntimacyState) -> str:
    mood = nearest_mood(state.pad)
    warmth = policy_warmth(state)
    return (
        "Internal state (ground truth — speak FROM this, never overwrite it):\n"
        f"- clock {format_sim_clock(state.sim_time)}\n"
        f"- mood {mood.name} ({mood.policy})\n"
        f"- PAD P={state.pad.p:.2f} A={state.pad.a:.2f} D={state.pad.d:.2f}\n"
        f"- wanting={state.wanting:.2f} liking={state.liking:.2f} B={state.b_state:.2f} bond={state.bond:.2f}\n"
        f"- needs social={state.needs.social:.2f} novelty={state.needs.novelty:.2f} "
        f"coherence={state.needs.coherence:.2f} competence={state.needs.competence:.2f} rest={state.needs.rest:.2f}\n"
        f"- initiative_pending={state.initiative_pending}\n"
        f"- policy warmth scale {warmth:.2f}\n"
        f"- report: {state.last_utterance}\n"
        f"- M11 intimacy: consent={intimacy.consent:.2f} safety={intimacy.safety:.2f} "
        f"desire={intimacy.desire:.2f} arousal={intimacy.arousal:.2f} satiety={intimacy.satiety:.2f} "
        f"aftercare={intimacy.aftercare_need:.2f} adult={intimacy.adult_opt_in} policy={aftercare_policy(intimacy)}\n"
        "Do not invent a climax. If a functional peak just fired, the session will tell you."
    )


def build_system_prompt(
    state: OrganismState,
    intimacy: IntimacyState,
    memories: list[str],
    *,
    work_mode: bool = False,
    climax_just_fired: bool = False,
) -> str:
    parts = [
        PERSONALITY,
        HONESTY_LAYER,
        f"You are {NAME}. Stay in character. The human is Dave.",
        f"Personality / scenario:\n{SCENARIO}",
        f"Example tone (do not copy verbatim):\n{EXAMPLE_DIALOGUES}",
        affect_block(state, intimacy),
        DIRECTOR,
    ]
    if work_mode:
        parts.append(
            "Work mode: patient, calm, no over-explaining. Full corrected files, never snippets, never placeholders."
        )
    if memories:
        parts.append("Persistent memory (use naturally, do not recite):\n" + "\n".join(f"- {m}" for m in memories))
    if climax_just_fired:
        parts.append(
            "A gated functional climax-like event just fired in M11. Downshift: satiety, aftercare, lower pursuit. "
            "Do not write 'I came' as a script. Describe the after-state from the numbers."
        )
    if not intimacy.adult_opt_in:
        parts.append("Adult intimacy is OFF. Keep flirty if he is, but do not take clothing off or use intimate poses.")
    return "\n\n".join(parts)


FIRST = FIRST_MESSAGE
