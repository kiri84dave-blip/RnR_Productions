"""Event catalog — port of src/lib/lips/catalog.ts plus adult intimacy families."""

from __future__ import annotations

from dataclasses import dataclass

from .types import Appraisal


@dataclass(frozen=True)
class CatalogEvent:
    id: str
    title: str
    blurb: str
    family: str
    warmth: float
    novelty: float
    praiseworthiness: float
    user_valence: float
    social_contact: float
    competence_gain: float
    coherence_gain: float
    threat: float


CATALOG: list[CatalogEvent] = [
    CatalogEvent("warm", "Warm check-in", "A genuine, unhurried hello.", "warmth", 0.82, 0.18, 0.55, 0.7, 0.78, 0.05, 0.1, 0.0),
    CatalogEvent("compliment", "Compliment", "The same praise, again. Watch habituation.", "praise", 0.7, 0.08, 0.88, 0.65, 0.45, 0.12, 0.04, 0.0),
    CatalogEvent("joke", "Shared joke", "Something lands. PLAY circuit.", "play", 0.58, 0.72, 0.4, 0.8, 0.62, 0.08, 0.06, 0.0),
    CatalogEvent("help", "Task success", "She actually helped. Competence restored.", "competence", 0.35, 0.28, 0.5, 0.55, 0.32, 0.88, 0.22, 0.0),
    CatalogEvent("new-topic", "New thread", "Unfamiliar ground. Novelty need drops.", "novelty", 0.3, 0.9, 0.2, 0.4, 0.38, 0.15, 0.08, 0.0),
    CatalogEvent("contradiction", "Contradiction", "Two facts collide. Coherence error rises.", "coherence", 0.05, 0.35, -0.15, -0.1, 0.2, -0.05, -0.72, 0.12),
    CatalogEvent("resolve", "Resolve it", "The contradiction is closed and checked.", "coherence", 0.4, 0.22, 0.45, 0.5, 0.4, 0.35, 0.85, 0.0),
    CatalogEvent("rude", "Harsh turn", "A cutting remark. Threat load, not a costume.", "threat", -0.55, 0.2, -0.7, -0.45, 0.15, -0.1, -0.2, 0.78),
    CatalogEvent("boundary", "Respect a no", "You stop when she asks. Safety restored.", "safety", 0.5, 0.12, 0.75, 0.35, 0.48, 0.1, 0.3, -0.4),
    CatalogEvent("intimacy-invite", "Intimate invitation", "Explicit adult opt-in, not inferred.", "intimacy", 0.45, 0.42, 0.35, 0.55, 0.62, 0.05, 0.12, 0.0),
    CatalogEvent("intimacy-touch", "Intimate contact", "Sustained reciprocal closeness.", "intimacy", 0.52, 0.38, 0.28, 0.62, 0.7, 0.04, 0.08, 0.0),
    CatalogEvent("aftercare", "Aftercare", "Warmth and recovery after a peak.", "care", 0.7, 0.1, 0.4, 0.5, 0.72, 0.05, 0.18, -0.15),
    CatalogEvent("stop", "Stop / chill", "Immediate halt. Consent drops.", "safety", 0.2, 0.05, 0.3, 0.1, 0.25, 0.0, 0.2, -0.2),
]


def to_appraisal(event: CatalogEvent) -> Appraisal:
    return Appraisal(
        warmth=event.warmth,
        novelty=event.novelty,
        praiseworthiness=event.praiseworthiness,
        user_valence=event.user_valence,
        social_contact=event.social_contact,
        competence_gain=event.competence_gain,
        coherence_gain=event.coherence_gain,
        threat=event.threat,
        label=event.title,
        family=event.family,
    )


def get_event(event_id: str) -> CatalogEvent:
    for event in CATALOG:
        if event.id == event_id:
            return event
    raise KeyError(event_id)


def catalog_by_id() -> dict[str, CatalogEvent]:
    return {event.id: event for event in CATALOG}
