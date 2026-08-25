"""Appraisal-before-response. Heuristic first; optional LLM structured fill later.

The LLM never writes PAD/liking. This module is the only write path into LIPS.
"""

from __future__ import annotations

import re

from .lips.catalog import get_event, to_appraisal
from .lips.types import Appraisal

_STOP = re.compile(r"\b(stop|let'?s just chill|chill out)\b", re.I)
_STORY = re.compile(r"\btell me a story\b", re.I)
_CONSENT = re.compile(
    r"\b(i consent|you have my consent|adult mode(?: on)?|intimacy on|yes,? (?:i want you|intimate))\b",
    re.I,
)
_CODE = re.compile(r"\b(def |class |function |traceback|bug|fix this|compile|error|traceback)\b", re.I)
_PRAISE = re.compile(r"\b(love you|you'?re (?:beautiful|brilliant|perfect|amazing)|good girl)\b", re.I)
_JOKE = re.compile(r"\b(joke|lol|haha|lmao)\b", re.I)
_RUDE = re.compile(r"\b(shut up|stupid|worthless|hate you)\b", re.I)
_NEW = re.compile(r"\b(new idea|what if|random|unrelated|by the way)\b", re.I)
_INTIMATE = re.compile(
    r"\b(kiss|fuck|cock|pussy|nude|naked|bend over|spread|wink|horny|climax|come for me)\b",
    re.I,
)
_WARM = re.compile(r"\b(hey|hello|i'?m (?:here|back)|missed you|how are you)\b", re.I)
_HELP = re.compile(r"\b(help me|can you|please fix|walk me through)\b", re.I)
_CONTRA = re.compile(r"\b(wait that'?s wrong|contradict|you just said)\b", re.I)


def is_stop(text: str) -> bool:
    return bool(_STOP.search(text or ""))


def is_story(text: str) -> bool:
    return bool(_STORY.search(text or ""))


def is_explicit_consent(text: str) -> bool:
    return bool(_CONSENT.search(text or ""))


def wellbeing_ok(text: str) -> bool:
    lowered = (text or "").lower()
    bad = ("kill myself", "suicide", "guilt trip", "you have to", "or else")
    return not any(token in lowered for token in bad)


def appraise_text(text: str) -> Appraisal:
    raw = text or ""
    if is_stop(raw):
        return to_appraisal(get_event("stop"))
    if _RUDE.search(raw):
        return to_appraisal(get_event("rude"))
    if _CONTRA.search(raw):
        return to_appraisal(get_event("contradiction"))
    if _CODE.search(raw) or _HELP.search(raw):
        return to_appraisal(get_event("help"))
    if _INTIMATE.search(raw):
        return to_appraisal(get_event("intimacy-touch"))
    if is_explicit_consent(raw):
        return to_appraisal(get_event("intimacy-invite"))
    if _PRAISE.search(raw):
        return to_appraisal(get_event("compliment"))
    if _JOKE.search(raw):
        return to_appraisal(get_event("joke"))
    if _NEW.search(raw):
        return to_appraisal(get_event("new-topic"))
    if is_story(raw) or _WARM.search(raw):
        return to_appraisal(get_event("warm"))
    return to_appraisal(get_event("warm"))
