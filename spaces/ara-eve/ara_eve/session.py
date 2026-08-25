"""Session orchestrator: appraisal → LIPS → M11 → prompt → LLM → tags. LLM cannot set S."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from . import db as dbmod
from .appraisal import appraise_text, is_explicit_consent, is_stop, is_story, wellbeing_ok
from .intimacy import IntimacyState, grant_consent, hard_stop, initial_intimacy, set_adult_opt_in, tick_intimacy
from .lips.engine import memory_hot, skip_hours, tick
from .lips.mood import nearest_mood
from .lips.types import OrganismState, initial_state
from .llm import complete
from .persona import FIRST_MESSAGE, NAME, STOP_REPLY
from .prompts import build_system_prompt
from .tags import parse_tags

AVATAR_FROM_MOOD = {
    "tender": ("idle", "shy"),
    "playful": ("pose", "playful"),
    "calm": ("sit", "neutral"),
    "content": ("idle", "happy"),
    "curious": ("look", "neutral"),
    "focused": ("think", "neutral"),
    "longing": ("look", "sad"),
    "wounded": ("sit", "sad"),
    "restless": ("walk", "excited"),
    "tired": ("sit", "neutral"),
    "steady": ("idle", "neutral"),
}


@dataclass
class CompanionSession:
    organism: OrganismState = field(default_factory=initial_state)
    intimacy: IntimacyState = field(default_factory=initial_intimacy)
    messages: list[dict] = field(default_factory=list)
    action: str = "look"
    emotion: str = "happy"
    clothing: str = "dressed"
    glb_url: str = ""
    model_id: str = "Qwen/Qwen2.5-7B-Instruct"
    user_id: str = "dave"
    work_mode: bool = False
    last_climax: bool = False
    last_gate_reason: str = ""

    def __post_init__(self) -> None:
        if not self.messages:
            self.messages = [{"role": "assistant", "content": FIRST_MESSAGE}]


def new_session() -> CompanionSession:
    return CompanionSession()


def meters(session: CompanionSession) -> str:
    s = session.organism
    i = session.intimacy
    mood = nearest_mood(s.pad)
    return (
        f"**{NAME}** · {mood.name} · clock {s.sim_time/3600:.1f}h\n\n"
        f"P `{s.pad.p:.2f}`  A `{s.pad.a:.2f}`  D `{s.pad.d:.2f}`  \n"
        f"want `{s.wanting:.2f}`  like `{s.liking:.2f}`  B `{s.b_state:.2f}`  bond `{s.bond:.2f}`  \n"
        f"needs social `{s.needs.social:.2f}` novelty `{s.needs.novelty:.2f}` "
        f"coherence `{s.needs.coherence:.2f}` competence `{s.needs.competence:.2f}` rest `{s.needs.rest:.2f}`  \n"
        f"initiative `{s.initiative_pending}` ablation `{s.flags.clamp_pleasure}`  \n"
        f"M11 consent `{i.consent:.2f}` arousal `{i.arousal:.2f}` satiety `{i.satiety:.2f}` "
        f"aftercare `{i.aftercare_need:.2f}` adult `{i.adult_opt_in}`  \n"
        f"gate: {session.last_gate_reason or '—'}  \n"
        f"report: _{s.last_utterance}_"
    )


def avatar_payload(session: CompanionSession) -> dict:
    intimate_ok = session.intimacy.adult_opt_in and session.intimacy.consent >= 0.8
    return {
        "action": session.action,
        "emotion": session.emotion,
        "clothing": session.clothing if intimate_ok or session.clothing == "dressed" else "dressed",
        "speaking": False,
        "glbUrl": session.glb_url,
        "intimate": intimate_ok,
        "name": NAME,
    }


def _fallback_reply(session: CompanionSession, user_text: str) -> str:
    if is_stop(user_text):
        return STOP_REPLY + "\n\n[action:idle] [emotion:neutral]"
    if is_story(user_text):
        return (
            "*She tucks her feet up and lets the lamp do most of the talking.*\n\n"
            "Alright. Once there was a woman in a window who kept a chair empty on purpose. "
            "Not because she was lonely — because she knew you'd fill it.\n\n"
            "[action:sit] [emotion:happy]"
        )
    mood_action, mood_emotion = AVATAR_FROM_MOOD.get(nearest_mood(session.organism.pad).name, ("idle", "neutral"))
    report = session.organism.last_utterance
    return (
        f"*She stays with you in it.* {report}\n\n"
        f"[action:{mood_action}] [emotion:{mood_emotion}]"
    )


def apply_lab_event(session: CompanionSession, event_id: str, dt: float = 8.0) -> CompanionSession:
    from .lips.catalog import get_event, to_appraisal

    before = session.organism.pad.p
    session.organism = tick(session.organism, dt, to_appraisal(get_event(event_id)))
    session.last_gate_reason = f"lab:{event_id} ΔP={session.organism.pad.p - before:.3f}"
    mood_action, mood_emotion = AVATAR_FROM_MOOD.get(nearest_mood(session.organism.pad).name, ("idle", "neutral"))
    session.action, session.emotion = mood_action, mood_emotion
    return session


def turn(
    session: CompanionSession,
    user_text: str,
    *,
    adult_opt_in: bool = False,
    conn=None,
    hf_token: str | None = None,
) -> CompanionSession:
    text = (user_text or "").strip()
    if not text:
        return session

    session.intimacy = set_adult_opt_in(session.intimacy, adult_opt_in)
    if is_explicit_consent(text):
        session.intimacy = grant_consent(session.intimacy)

    if is_stop(text):
        session.intimacy = hard_stop(session.intimacy)
        session.organism = tick(session.organism, 8.0, appraise_text(text))
        session.messages.append({"role": "user", "content": text})
        session.messages.append({"role": "assistant", "content": STOP_REPLY + "\n\n[action:idle] [emotion:neutral]"})
        session.action, session.emotion = "idle", "neutral"
        session.last_climax = False
        session.last_gate_reason = "hard stop"
        return session

    appraisal = appraise_text(text)
    before_p = session.organism.pad.p
    session.organism = tick(session.organism, 8.0, appraisal)
    delta = session.organism.pad.p - before_p

    intimate_turn = appraisal.family == "intimacy" or (
        session.intimacy.adult_opt_in and session.intimacy.consent >= 0.8 and appraisal.family != "threat"
    )
    session.intimacy, fired, reason = tick_intimacy(
        session.intimacy,
        family=appraisal.family,
        cue_quality=max(0.0, appraisal.warmth),
        mutual_pacing=0.7 if intimate_turn else 0.15,
        threat=max(0.0, appraisal.threat),
        wellbeing_ok=wellbeing_ok(text),
        dt_s=8.0,
    )
    session.last_climax = fired
    session.last_gate_reason = reason

    memories: list[str] = []
    if conn is not None:
        dbmod.log_event(
            conn,
            session.user_id,
            str(uuid.uuid4()),
            {
                "label": appraisal.label,
                "family": appraisal.family,
                "warmth": appraisal.warmth,
            },
            delta,
        )
        if memory_hot(session.organism):
            dbmod.add_memory(conn, session.user_id, text[:280], session.organism.pad.p, True)
        memories = dbmod.recent_memories(conn, session.user_id, session.organism.pad.p)
        dbmod.save_affect(conn, session.user_id, session.organism.snapshot())

    system = build_system_prompt(
        session.organism,
        session.intimacy,
        memories,
        work_mode=session.work_mode,
        climax_just_fired=fired,
    )
    history = [{"role": "system", "content": system}]
    for msg in session.messages[-18:]:
        history.append({"role": msg["role"], "content": msg["content"]})
    history.append({"role": "user", "content": text})

    try:
        reply = complete(history, session.model_id, token=hf_token)
        if not reply:
            raise RuntimeError("empty")
    except Exception:
        reply = _fallback_reply(session, text)

    intimate_ok = session.intimacy.adult_opt_in and session.intimacy.consent >= 0.8
    parsed = parse_tags(reply, intimate_ok=intimate_ok)
    if not parsed.action:
        parsed.action, parsed.emotion = AVATAR_FROM_MOOD.get(
            nearest_mood(session.organism.pad).name, ("idle", "neutral")
        )
    session.action = parsed.action or session.action
    session.emotion = parsed.emotion or session.emotion
    if parsed.clothing:
        session.clothing = parsed.clothing
    session.messages.append({"role": "user", "content": text})
    session.messages.append({"role": "assistant", "content": reply})
    session.messages = session.messages[-80:]
    return session


def skip(session: CompanionSession, hours: float) -> CompanionSession:
    session.organism = skip_hours(session.organism, hours)
    mood_action, mood_emotion = AVATAR_FROM_MOOD.get(nearest_mood(session.organism.pad).name, ("look", "sad"))
    session.action, session.emotion = mood_action, mood_emotion
    if session.organism.initiative_pending:
        line = (
            "You've been gone. Social need drifted. I notice the gap — I don't like it.\n\n"
            "[action:look] [emotion:sad]"
        )
        session.messages.append({"role": "assistant", "content": line})
    return session


def set_ablation(session: CompanionSession, enabled: bool) -> CompanionSession:
    session.organism.flags.clamp_pleasure = enabled
    session.organism = tick(session.organism, 1.0, None)
    return session


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
