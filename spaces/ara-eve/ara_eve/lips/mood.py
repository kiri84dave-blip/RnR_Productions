"""PAD mood atlas — port of src/lib/lips/mood.ts."""

from __future__ import annotations

from dataclasses import dataclass

from .types import Pad


@dataclass(frozen=True)
class MoodEntry:
    name: str
    pad: Pad
    policy: str


MOOD_ATLAS: list[MoodEntry] = [
    MoodEntry("tender", Pad(0.62, 0.18, -0.12), "soft, close, unhurried"),
    MoodEntry("playful", Pad(0.48, 0.58, 0.22), "light, teasing, initiative-ready"),
    MoodEntry("calm", Pad(0.28, -0.38, 0.12), "even, spacious, low urgency"),
    MoodEntry("content", Pad(0.42, -0.08, 0.18), "warm without chasing"),
    MoodEntry("curious", Pad(0.22, 0.42, 0.28), "asks, follows threads, seeks novelty"),
    MoodEntry("focused", Pad(0.08, 0.22, 0.52), "precise, task-forward"),
    MoodEntry("longing", Pad(-0.18, 0.32, -0.42), "reaches first, names absence"),
    MoodEntry("wounded", Pad(-0.48, 0.38, -0.28), "boundary-first, shorter replies"),
    MoodEntry("restless", Pad(-0.12, 0.48, 0.08), "bored, proposes a shift"),
    MoodEntry("tired", Pad(-0.08, -0.42, -0.18), "protects rest, declines extra load"),
    MoodEntry("steady", Pad(0.12, 0.04, 0.08), "baseline, neither chasing nor withdrawing"),
]


def nearest_mood(pad: Pad) -> MoodEntry:
    best = MOOD_ATLAS[0]
    best_dist = float("inf")
    for mood in MOOD_ATLAS:
        dp = pad.p - mood.pad.p
        da = pad.a - mood.pad.a
        dd = pad.d - mood.pad.d
        dist = dp * dp + da * da + dd * dd
        if dist < best_dist:
            best_dist = dist
            best = mood
    return best
